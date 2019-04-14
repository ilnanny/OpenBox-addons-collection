/*
 * vera-plugin-openbox - openbox plugin for vera
 * Copyright (C) 2014  Eugenio "g7" Paolantonio and the Semplice Project
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Authors:
 *     Eugenio "g7" Paolantonio <me@medesimo.eu>
*/

/*
 * Currently compton supports the on-the-fly change of the following properties:
 * 
 * fade_delta
 * fade_in_step
 * fade_out_step
 * no_fading_openclose
 * uredir_if_possible
 * clear_shadow
 * track_focus
 * vsync
 * redirected_force
*/

using Vera;

namespace OpenboxPlugin {

	public class Compton : Object {
		
		/**
		 * This class handles the startup and the settings of the
		 * compton compositor.
		 * 
		 * Any change done via dconf will be applied on-the-fly on
		 * comtpon via DBus.
		*/
		
		// Ugly but works.
		//private string DISPLAY = Environment.get_variable("DISPLAY").replace(":","_").replace(".","_");
		private string DISPLAY = Environment.get_variable("DISPLAY").replace(":","_").split(".")[0];
		
		private Settings settings;
		private ComptonConfiguration compton_settings;
		private DBusProxy compton_proxy;
		
		private Launcher compton_launcher;
		private Pid? compton_pid = null;
		
		private uint queue_timeout = 0;
		private HashTable<string, Variant> queue = new HashTable<string, Variant>(str_hash, str_equal);
		
		private void launch_compton(string configuration_file_) {
			/**
			 * Launches compton.
			*/

			string configuration_file = configuration_file_.replace(
				"~",
				Environment.get_home_dir()
			);
			
			/* FIXME: Enable respawn */
			
			this.compton_launcher = new Launcher(
				{ "compton", "--dbus", "--config", configuration_file },
				false,
				false
			);
			
			try {
				this.compton_pid = this.compton_launcher.launch();
			} catch (Error e) {
				warning("Unable to launch compton!");
			}
			
		}
		
		private void on_settings_changed(string key) {
			/**
			 * Fired when a setting has been changed.
			 * 
			 * We will make compton aware of the change via DBus.
			*/
			
			// Process non-compton keys...
			if (key == "enable-visual-effects") {
				// Enable visual effects.
				
				if (this.settings.get_boolean("enable-visual-effects") && this.compton_pid == null) {
					this.launch_compton(this.settings.get_string("configuration-file"));
				} else {
					Posix.kill(this.compton_pid, Posix.SIGTERM);
					Process.close_pid(this.compton_pid);
					
					this.compton_pid = null;
				}
				
				return;
			} else if (key == "configuration-file") {
				// Configuration file.
				
				this.compton_settings.configuration_file = this.settings.get_string(key);
				this.compton_settings.reload();
				this.syncronize_dconf();
				
				return;
			}
			
			/* Add to queue */
			this.queue.set(key, this.settings.get_value(key));
			
			/* Add timer */
			if (this.queue_timeout > 0) {
				/* Timeout is already present, we should cancel it and add another */
				Source.remove(this.queue_timeout);
			}
			this.queue_timeout = Timeout.add(700, this.on_queue_timeout_elapsed);
		
		}
		
		private bool on_queue_timeout_elapsed() {
			/**
			 * Fired when the queue timeout has been elapsed and we thus
			 * need to apply the settings
			*/
			
			bool reset = false;
			
			lock (this.compton_settings) {
			
				this.queue.foreach_remove(
					(key, value) => {
						/* Apply */
						if (this.apply_setting(key, value)) {
							reset = true;
						}
						
						return true; /* remove */
					}
				);
				
				/* Dump, finally */
				this.compton_settings.dump();
				
			}
			
			if (reset) {
				try {
					this.compton_proxy.call_sync("reset", null, DBusCallFlags.NONE, 1000, null);
				} catch (Error e) {
					warning("Unable to reset compton.");
				}
			}
			
			/* Reset timeout to 0, the source will be removed automatically by GLib */
			this.queue_timeout = 0;
			
			return false;
		}
		
		private bool apply_setting(string key, Variant val) {
			/**
			 * Applies the settings to compton.
			 * The setting will be stored in memory into the ComptonConfiguration
			 * object and eventually set via DBus if the given setting supports
			 * it.
			 * 
			 * Returns True if a compton reset is necessary, False if not.
			*/
			
			/*
			 * We need to create a new Variant composed of the key and
			 * the value.
			 * We get the value via Settings.get_value() and then we build
			 * another Variant using the informations for the Variant now
			 * obtained.
			 * 
			 * I'm sure there is a better way to do this, but I haven't
			 * found one yet.
			*/
			Variant new_variant;
			
			// Properties have underscores instead of a dash
			string new_key = key.replace("-","_");
			
			switch (val.get_type_string()) {
				
				case "s":
					// String
					new_variant = new Variant("(ss)", new_key, val.get_string());
					this.compton_settings.set_string(key, val.get_string());
					
					break;
				case "b":
					// Boolean
					new_variant = new Variant("(sb)", new_key, val.get_boolean());
					this.compton_settings.set_bool(key, val.get_boolean());
					
					break;
				case "d":
					// Double
					new_variant = new Variant("(sd)", new_key, val.get_double());
					this.compton_settings.set_double(key, val.get_double());
					
					break;
				case "i":
					// int32
					new_variant = new Variant("(si)", new_key, val.get_int32());
					this.compton_settings.set_int(key, val.get_int32());
					
					break;
				default:
					// Breaking
					message("Returning...");
					return false;
			}
			
			try {
				this.compton_proxy.call_sync("opts_set", new_variant, DBusCallFlags.NONE, 1000, null);
			} catch (Error e) {
				/* Tell caller that a reload is necessary */
				return true;
			}
			
			return false;
		}
		
		private void syncronize_dconf(bool reverse = false) {
			/**
			 * This method syncronizes the contents of the settings
			 * in dconf with the configuration in this.compton_settings.
			*/
			
			Variant val;
			foreach (string key in this.settings.list_keys()) {
				
				if (key == "enable-visual-effects" || key == "configuration-file") {
					/* Skip */
					continue;
				}
				
				val = this.settings.get_value(key);
				
				switch (val.get_type_string()) {
					case "s":
						// String
						
						if (!reverse) {
						
							string? result = this.compton_settings.get_string(key);
							
							if (result != null && result != val.get_string())
								this.settings.set_string(key, result);
								
						} else {
							
							this.compton_settings.set_string(key, val.get_string());
							
						}
						
						break;
					case "b":
						// Boolean
						
						if (!reverse) {
							
							bool? result = this.compton_settings.get_bool(key);
							
							if (result != null && result != val.get_boolean())
								this.settings.set_boolean(key, result);
						
						} else {
							
							this.compton_settings.set_bool(key, val.get_boolean());
							
						}
						
						break;
					case "d":
						// Double
						
						if (!reverse) {
							
							double? result = this.compton_settings.get_double(key);
							
							if (result != null && result != val.get_double())
								this.settings.set_double(key, result);
						
						} else {
							
							this.compton_settings.set_double(key, val.get_double());
							
						} 
						
						break;
					case "i":
						// int32
						
						if (!reverse) {
							
							int? result = this.compton_settings.get_int(key);
							
							if (result != null && result != val.get_int32())
								this.settings.set_int(key, result);
						
						} else {
							
							this.compton_settings.set_int(key, val.get_int32());
							
						}
						
						break;
				}
			}
			
			if (reverse)
				/* Dump */
				this.compton_settings.dump();
			
		}
		
		public Compton() {
			/**
			 * Constructs the object.
			*/
			
			/*
			 * I *love* vala's way to interface with DBus services.
			 * But it seems that that way doesn't work here.
			 * Compton doesn't export opts_set() so we can't interface
			 * with it.
			 * I'm no DBus expert, so I don't know if their way is ideal,
			 * probably yes.
			 * Anyway, by creating a new DBusProxy we can use call_sync()
			 * to use opts_set().
			 * Good, isn't it?
			*/
						
			this.settings = new Settings("org.semplicelinux.vera.compton");
			
			// Read compton settings
			string configuration_file = this.settings.get_string("configuration-file").replace(
				"~",
				Environment.get_home_dir()
			);
			
			bool initial_setup = false;
			if (!FileUtils.test(configuration_file, FileTest.EXISTS)) {
				/* Create empty file */
				
				try {
					File file = File.new_for_path(configuration_file);
					if (!file.get_parent().query_exists()) {
						file.get_parent().make_directory_with_parents();
					}
					
					file.create(FileCreateFlags.NONE);
				} catch (Error e) {
					warning(e.message);
					return;
				}
				
				initial_setup = true;
			}
				
			this.compton_settings = new ComptonConfiguration(configuration_file);
			
			// Syncronize dconf with the compton.conf
			if (initial_setup)
				/* FIXME: two-way syncronization (initial_setup = false) disabled for now */
				this.syncronize_dconf(initial_setup);
			
			/* Launch! */
			if (this.settings.get_boolean("enable-visual-effects"))
				this.launch_compton(configuration_file);
						
			// Ensure we are aware when settings change...
			this.settings.changed.connect(this.on_settings_changed);
			
			/*
			 * FIXME: GSettings doesn't properly report changed settings
			 * if a connection on them hasn't been estabilished before.
			 * It's possible to estabilish one by reading every setting
			 * one-by-one (as we need a callback for every setting).
			 * 
			 * BEWARE. It's ugly!
			*/
			foreach (string key in this.settings.list_keys()) {
				Variant val = this.settings.get_value(key);
			}
			
			Timeout.add_seconds(
				2,
				() => {
					this.compton_proxy = new DBusProxy.for_bus_sync(
						BusType.SESSION,
						DBusProxyFlags.NONE,
						null,
						"com.github.chjj.compton." + DISPLAY,
						"/",
						"com.github.chjj.compton",
						null
					);
					
					return false;
				}
			);
		}
		
	}
			

}

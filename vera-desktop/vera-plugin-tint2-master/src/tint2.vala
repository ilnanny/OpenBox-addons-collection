/*
 * vera-plugin-tint2 - tint2 plugin for vera
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

using Vera;

namespace Tint2Plugin {

	public class Plugin : Peas.ExtensionBase, VeraPlugin {

		private string HOME = Environment.get_home_dir();

		public XlibDisplay display;
		public Settings settings;
			
		private void on_process_terminated(Pid pid, int status) {
			/**
			 * Fired when the process pid has been terminated.
			 */
			
			debug("Pid %s terminated.", pid.to_string());
			
			Process.close_pid(pid);
			
			if (status > 1)
				this.startup(StartupPhase.PANEL);
		}

		public void init(Display display) {
			/**
			 * Initializes the plugin.
			 */
			
			try {
				this.display = (XlibDisplay)display;
					
				this.settings = new Settings("org.semplicelinux.vera.tint2");

			} catch (Error ex) {
				error("Unable to load plugin settings.");
			}

			
		}
		
		public void startup(StartupPhase phase) {
			/**
			 * Called by vera when doing the startup.
			 */
			
			if (phase == StartupPhase.PANEL || phase == StartupPhase.SESSION) {
				/* Launch tint2. */
				
				/* Delay startup if we are on live */
				if (FileUtils.test("/etc/semplice-live-mode", FileTest.EXISTS) && phase == StartupPhase.PANEL) {
					Timeout.add_seconds(
						5,
						() => {
							this.startup(StartupPhase.SESSION);
							
							return false;
						}
					);
					
					return;
				}
				
				Pid pid;
				
				try {
				
					if (this.settings.get_boolean("first-start")) {
						/* First start */
						DateTime local = new DateTime.now_local();
						if (local.format("%p") != "") {
							/* This timezone uses AM/PM, properly
							 * set it in the panel's secondary_configuration */
							
							File secondary_config = File.new_for_path(
								Path.build_filename(this.HOME, ".config/tint2", "secondary_config")
							);
							
							File directory = secondary_config.get_parent();
							if (!directory.query_exists())
								directory.make_directory_with_parents();
							
							FileIOStream io_stream;
							if (!secondary_config.query_exists())
								io_stream = secondary_config.create_readwrite(FileCreateFlags.PRIVATE);
							else
								io_stream = secondary_config.open_readwrite();
							
							FileOutputStream stream = io_stream.output_stream as FileOutputStream;
							
							size_t written;
							stream.write_all("time1_format = %I:%M %p\npanel_items = TSC\n".data, out written);
							stream.close();
						}
						
						this.settings.set_boolean("first-start", false);
						
					}
				
				} catch (Error e) {
					warning("Unable to set-up the secondary_config: %s", e.message); 
				}
				
				/* Check for the configuration_file */
				string configuration_file = this.settings.get_string("configuration-file");
				if (!FileUtils.test(configuration_file, FileTest.EXISTS))
					/* It doesn't exist, use the default configuration file */
					configuration_file = "/etc/xdg/tint2/tint2rc";
				
				try {
					Process.spawn_async(
						this.HOME,
						{ "tint2", "-c", configuration_file },
						Environ.get(),
						SpawnFlags.SEARCH_PATH | SpawnFlags.DO_NOT_REAP_CHILD,
						null,
						out pid
					);
										
					ChildWatch.add(pid, this.on_process_terminated);
				} catch (SpawnError e) {
					warning(e.message);
				}
				
			}
			
		}
		
		/* FIXME */
		public void shutdown() {}
		

	}
}

[ModuleInit]
public void peas_register_types(GLib.TypeModule module)
{
	Peas.ObjectModule objmodule = module as Peas.ObjectModule;
	objmodule.register_extension_type(typeof(VeraPlugin), typeof(Tint2Plugin.Plugin));
}

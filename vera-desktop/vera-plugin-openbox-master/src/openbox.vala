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

using Vera;

namespace OpenboxPlugin {

	public class Plugin : Peas.ExtensionBase, VeraPlugin {

		private string HOME = Environment.get_home_dir();
		
		/* FIXME: Maybe something configurable? */
		private string openbox_config_file;

		public Display display;
		public Settings settings;

		private Compton compton;
		private OpenboxConfiguration configuration;
		
		private void on_process_terminated(Pid pid, int status) {
			/**
			 * Fired when the process pid has been terminated.
			*/
			
			debug("Pid %s terminated.", pid.to_string());
			
			Process.close_pid(pid);
		}

		public void init(Display display) {
			/**
			 * Initializes the plugin.
			*/
			
			try {
				this.display = display;
				this.settings = new Settings("org.semplicelinux.vera.openbox");
				
				/* Build the file path */
				this.openbox_config_file = this.settings.get_string("config-path").replace(
					"~",
					HOME
				);
				
				this.compton = new Compton();

			} catch (Error ex) {
				error("Unable to load plugin settings.");
			}

			
		}
		
		public void startup(StartupPhase phase) {
			/**
			 * Called by vera when doing the startup.
			*/
			
			if (phase == StartupPhase.WM) {
				
				/* Check for openbox_config_file */
				try {
					
					if (!FileUtils.test(this.openbox_config_file, FileTest.EXISTS)) {
						/* If it doesn't exist, copy from the data directory */
						File origin = File.new_for_path("/usr/share/vera-plugin-openbox/rc.xml");
						File destination = File.new_for_path(this.openbox_config_file);
						
						/* Create target directory if it doesn't exist */
						File destination_directory = destination.get_parent();
						if (!destination_directory.query_exists())
							destination_directory.make_directory_with_parents();
						
						origin.copy(destination, FileCopyFlags.NONE);
					}
					
				} catch (Error e) {
					
					warning("Unable to check for the existence of the Openbox configuration file.");
					this.openbox_config_file = "/usr/share/vera-plugin-openbox/rc.xml";
					
				}

				this.configuration = new OpenboxConfiguration(this.display, this.settings, this.openbox_config_file);
				
				// Launch openbox.
				Pid pid;
				
				try {
					Process.spawn_async(
						this.HOME,
						{ "openbox", "--config-file", this.openbox_config_file },
						Environ.get(),
						SpawnFlags.SEARCH_PATH | SpawnFlags.DO_NOT_REAP_CHILD,
						null,
						out pid
					);
										
					ChildWatch.add(pid, this.on_process_terminated);
					
					/*
					 * Wait half a second so that openbox can get
					 * ownership of the session.
					 * FIXME: We shouldn't do that and rely on events
					 * instead. See vera bug #1.
					*/
					Thread.usleep(500000);
				} catch (SpawnError e) {
					warning(e.message);
				}
			}
			
		}
		
		public void shutdown() {
			/**
			 * Shutdown method, that will not do anything because
			 * this plugin is not meant to be hot-unloaded.
			*/
			
		}
		

	}
}

[ModuleInit]
public void peas_register_types(GLib.TypeModule module)
{
	Peas.ObjectModule objmodule = module as Peas.ObjectModule;
	objmodule.register_extension_type(typeof(VeraPlugin), typeof(OpenboxPlugin.Plugin));
}

/*
 * vera - a simple, lightweight, GTK3 based desktop environment
 * Copyright (C) 2014  Eugenio "g7" Paolantonio and the Semplice Project
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Authors:
 *     Eugenio "g7" Paolantonio <me@medesimo.eu>
*/

using Vera;

namespace AutostartPlugin {

	public class Application : GLib.Object {
		
		private KeyFile file = new KeyFile();
		public string name { get; private set; }
		public string executable { get; private set; }
		public StartupPhase phase { get; private set; }
		
		public Application(string path) {
			/**
			 * Creates a new Application object by reading the .desktop
			 * file specified in path.
			 */
			
			try {
				// load desktop file
				this.file.load_from_file(path, KeyFileFlags.NONE);
				
				this.name = this.file.get_string("Desktop Entry", "Name");
				this.executable = this.file.get_string("Desktop Entry", "Exec");
				if (this.file.has_key("Desktop Entry", "X-Vera-Autostart-Phase")) {
					switch (this.file.get_string("Desktop Entry", "X-Vera-Autostart-Phase")) {
						
						case "Initialization":
							this.phase = StartupPhase.INIT;
							break;
						case "WindowManager":
							this.phase = StartupPhase.WM;
							break;
						case "Panel":
							this.phase = StartupPhase.PANEL;
							break;
						case "Desktop":
							this.phase = StartupPhase.DESKTOP;
							break;
						case "Applications":
							this.phase = StartupPhase.OTHER;
							break;
					}
				} else {
					// No phase specified? Default to OTHER
					this.phase = StartupPhase.OTHER;
				}
			} catch {
				warning("Unable to properly parse desktop file %s.".printf(path));
			}
		}
	
	}


}

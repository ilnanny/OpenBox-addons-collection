/*
 * vera-plugin-power - power plugin for vera
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

namespace PowerPlugin {

	public class PowerTray : Gtk.Window {
		/**
		 * This class represents the Tray icon of a battery.
		*/
		
		private HashTable<string, Up.Device> paths = new HashTable<string, Up.Device>(str_hash, str_equal);
		
		private Gtk.StatusIcon status;
		private PowerMenu menu;
		//private PowerPreferencesMenu preferences;
		
		private Up.Client client;
		
		private void update_tray(Up.Device device) {
			/**
			 * Updates the tray icon.
			*/

			string icon, text_status, text_time, tooltip;
			
			/* Update tray icon */
			icon = Common.get_battery_icon(device);
			text_status = Common.get_battery_status_with_percentage(device);
						
			this.status.set_from_icon_name(icon);
			
			/* Build and set text */
			tooltip = text_status;
			
			text_time = Common.get_remaining_time(device);
			if (text_time != null) {
				tooltip += @", $text_time remaining";
			}
			
			this.status.set_tooltip_text(tooltip);
			
		}
		
		private void on_device_removed(string device) {
			/**
			 * Fired when a device has been removed.
			*/
			
			/* FIXME: Also handle the tray */
			this.menu.remove_device(this.paths.get(device));
			
		}
		
		private void update_informations(Up.Device device) {
			/**
			 * Updates the icon tray with informations on the
			 * current battery state.
			*/
			
			/*
			 * We now need to update the tray icon.
			 * We look only at the main battery.
			*/
						
			if (device.power_supply && device.kind == Up.DeviceKind.BATTERY) {
				this.update_tray(device);
			}
			
			if (device.is_present && device.kind != Up.DeviceKind.LINE_POWER) {
				/* Also update the menu */
				this.menu.update_device(device);
			}

		}
		
		private void open_popup(uint button = 0, uint time = Gtk.get_current_event_time()) {
			/**
			 * Opens the menu.
			*/
			
			this.menu.popup(null, null, null, button, time);
			
		}
		
		/*
		private void open_preferences(uint button, uint time) {
			/**
			 * Opens the preferences menu.
			/
			
			this.preferences.popup(null, null, null, button, time);
			
		}
		*/
	
		public PowerTray(Up.Client client) {
			/**
			 * Construct the PowerTray.
			*/
			
			Object();
			
			this.status = new Gtk.StatusIcon();
			
			this.menu = new PowerMenu();
			this.status.activate.connect(() => { this.open_popup(); });
			
			//this.preferences = new PowerPreferencesMenu();
			this.status.popup_menu.connect(this.open_popup);
			
			this.status.set_visible(true);
			
			this.client = client;
			
			/* Build informations... */
			this.client.get_devices().foreach(
				(device) => {
					this.paths.set(device.get_object_path(), device);
					
					this.update_informations(device);
					device.notify.connect(
						(s, p) => {
							/* Nested lambdas, yay! */
							this.update_informations(device);
						}
					);
				}
			);
			
			/* Connect things up */
			this.client.device_added.connect(this.update_informations);
			this.client.device_removed.connect(this.on_device_removed);
			
		}
		
	}

}

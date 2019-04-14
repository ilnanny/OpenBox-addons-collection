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

	public class Common : Object {
		/**
		 * Common static methods.
		*/

		public const uint FULL_THRESHOLD = 90;
		public const uint GOOD_THRESHOLD = 40;
		public const uint LOW_THRESHOLD = 15;
		public const uint EMPTY_THRESHOLD = 5;
		public const uint SAFE_HIBERNATE_THRESHOLD = 2;
		
		public static string get_remaining_time(Up.Device device) {
			/**
			 * Parses the given time (in seconds), and returns
			 * an appropriate estimation.
			*/
			
			string result = "";
			
			int64? time = null;
			if (device.state == Up.DeviceState.CHARGING) {
				time = device.time_to_full;
			} else if (device.state == Up.DeviceState.DISCHARGING) {
				time = device.time_to_empty;
			}
			
			if (time == null || time == 0) {
				return (string)null;
			}
			
			int64 time_ = time / 60;
			int64 hours = ((int64)Math.floor(time_ / 60));
			
			if (hours >= 1) {
				/* Hours! */
				result += "%lld %s".printf(
					hours,
					(hours == 1) ?
						_("hour") :
						_("hours")
				);
				time_ -= hours * 60;
			}
			if (time_ > 0) {
				/* Minutes */
				result += "%s%lld %s".printf(
					(hours >= 1) ? /* Separator */
						" " :
						"",
					time_,
					(time_ == 1) ?
						_("minute") :
						_("minutes")
				);
			}
			
			return result;
		}
		
		public static string get_battery_icon(Up.Device device) {
			/**
			 * Returns an icon name for the given battery state.
			*/
			
			string icon;
			
			/* Update tray icon */
			if (device.percentage >= FULL_THRESHOLD) {
				icon = "battery-full";
			} else if (device.percentage >= GOOD_THRESHOLD) {
				icon = "battery-good";
			} else if (device.percentage >= LOW_THRESHOLD) {
				icon = "battery-low";
			} else {
				icon = "battery-empty";
			}
			
			if (device.state == Up.DeviceState.CHARGING) {
				/* If we are charging, appropriate icon */
				icon = icon + "-charging";
			} else if (device.state == Up.DeviceState.FULLY_CHARGED) {
				/* Fully charged, yay */
				icon = icon + "-charged";
			}
			
			return icon;
		}
		
		public static string get_battery_status(Up.Device device) {
			/**
			 * Returns a (translated) battery status string.
			*/
			
			string status;
			
			switch (device.state) {
				
				case Up.DeviceState.CHARGING:
					status = _("Charging");
					break;
				
				case Up.DeviceState.FULLY_CHARGED:
					status = _("Fully charged");
					break;
				
				case Up.DeviceState.DISCHARGING:
					status = _("Discharging");
					break;
				
				case Up.DeviceState.EMPTY:
					status = _("Empty");
					break;
				
				default:
					status = _("Unknown");
					break;
			
			}
			
			return status;
			
		}
		
		public static string get_battery_status_with_percentage(Up.Device device) {
			/**
			 * Returns a (translated) battery status string, with percentage.
			*/
			
			string status = get_battery_status(device);
			
			if (device.is_present)
				status += @" ($(device.percentage)%)";
			
			return status;
			
		}
		
		public static string get_device_icon(Up.Device device) {
			/**
			 * Returns an icon name for the given device.
			*/
			
			string icon = null;
			
			/*
			 * Not implemented yet.
			
			switch (device.kind) {
				
				case Up.DeviceKind.BATTERY:
					
					icon = "computer-laptop";
					break;
					
			}
			 *
			*/
			
			return icon;
		}
	}

}

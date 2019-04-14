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
 * FIXMEs:
 *  - Maybe create a DBus service to reload() the configuration?
*/

namespace OpenboxPlugin {

	public class ComptonConfiguration : Object {
		
		/**
		 * This class tries to wrap the settings specified in the
		 * compton.conf.
		 * 
		 * When a setting is changed via the public API, it will be
		 * automatically written back in the configuration file.
		*/
				
		public bool enabled { get; private set; }
		
		public string configuration_file {get; set;}
		
		public LibConfig.Config configuration_object;
		
		public ComptonConfiguration(string configuration_file) {
			/**
			 * Construct the object.
			*/
			
			this.configuration_file = configuration_file;
			
			this.configuration_object = LibConfig.Config();
			
			this.reload();
			
		}
		
		public LibConfig.Setting lookup_or_create(string key, LibConfig.SettingType type) {
			/**
			 * Lookups for the key, and if it doesn't exist, it creates
			 * a new one.
			 * 
			 * It returns the found (or newly created) key or, if an
			 * error occurred, null.
			*/
			
			LibConfig.Setting result = this.configuration_object.lookup(key);
			
			if (result == null) {
				/* Not found */
				result = this.configuration_object.get_root_setting().add(
					key,
					type
				);
			}
			
			return result;
			
		}

		public void reload() {
			/**
			 * (Re)loads the configuration.
			*/
			
			/* There aren't methods in vala to expand user's path. WTF */
			configuration_file = this.configuration_file.replace(
				"~",
				Environment.get_home_dir()
			);
						
			if (!this.configuration_object.read_file(configuration_file)) {
				/* Error */
				warning("Unable to read compton configuration file %s.", configuration_file);
				this.enabled = false;
				
				return;
			} else {
				this.enabled = true;
			}
			
		}
		
		public bool? get_bool(string key) {
			/**
			 * Reads the key, and returns its value
			 * as a boolean.
			 * 
			 * If the key doesn't exists, it'll return null.
			*/
			
			if (!this.enabled) return null;
			
			LibConfig.Setting setting = this.configuration_object.lookup(key);
			
			if (setting != null)
				return setting.get_bool();
			else
				return null;
		}
		
		public void set_bool(string key, bool value) {
			/**
			 * Stores the value in the configuration file.
			*/
			
			if (!this.enabled) return;
			
			LibConfig.Setting setting = this.lookup_or_create(key, LibConfig.SettingType.BOOL);
			
			if (!(setting != null && setting.set_bool(value))) {
				warning("Unable to set key %s in the compton configuration file.", key);
			}
		}
		
		public string? get_string(string key) {
			/**
			 * Reads the key, and returns its value.
			 * 
			 * If the key doesn't exists, it'll return null.
			*/
			
			if (!this.enabled) return null;
			
			LibConfig.Setting setting = this.configuration_object.lookup(key);
			
			if (setting != null)
				return setting.get_string();
			else
				return null;
		}

		public void set_string(string key, string value) {
			/**
			 * Stores the value in the configuration file.
			*/
			
			if (!this.enabled) return;
			
			LibConfig.Setting setting = this.lookup_or_create(key, LibConfig.SettingType.STRING);
			
			if (!(setting != null && setting.set_string(value))) {
				warning("Unable to set key %s in the compton configuration file.", key);
			}
		}	

		public int? get_int(string key) {
			/**
			 * Reads the key, and returns its value
			 * as an integer.
			 * 
			 * If the key doesn't exists, it'll return null.
			*/
			
			if (!this.enabled) return null;
			
			LibConfig.Setting setting = this.configuration_object.lookup(key);
			
			if (setting != null)
				return setting.get_int();
			else
				return null;
		}

		public void set_int(string key, int value) {
			/**
			 * Stores the value in the configuration file.
			*/
			
			if (!this.enabled) return;
			
			LibConfig.Setting setting = this.lookup_or_create(key, LibConfig.SettingType.INT);
			
			if (!(setting != null && setting.set_int(value))) {
				warning("Unable to set key %s in the compton configuration file.", key);
			}
		}
		
		
		public double? get_double(string key) {
			/**
			 * Reads the key, and returns its value
			 * as a double.
			 * 
			 * If the key doesn't exists, it'll return null.
			*/
			
			if (!this.enabled) return null;
			
			LibConfig.Setting setting = this.configuration_object.lookup(key);
			
			if (setting != null)
				return setting.get_float();
			else
				return null;
		}

		public void set_double(string key, double value) {
			/**
			 * Stores the value in the configuration file.
			*/
			
			if (!this.enabled) return;
			
			LibConfig.Setting setting = this.lookup_or_create(key, LibConfig.SettingType.FLOAT);
			
			if (!(setting != null && setting.set_float((float)value))) {
				warning("Unable to set key %s in the compton configuration file.", key);
			}
		}
		
		
		public void dump() {
			/**
			 * Writes the new configuration in the configuration_file.
			*/
			
			if (!this.enabled) return;
			
			/* There aren't methods in vala to expand user's path. WTF */
			configuration_file = this.configuration_file.replace(
				"~",
				Environment.get_home_dir()
			);
						
			if (!this.configuration_object.write_file(configuration_file)) {
				/* Error */
				warning("Unable to write to the compton configuration file %s.", configuration_file);
				
				return;
			}
						
		}
	}
			

}

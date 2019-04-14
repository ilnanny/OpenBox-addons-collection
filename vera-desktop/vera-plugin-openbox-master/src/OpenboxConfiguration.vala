/*
 * vera-plugin-openbox - openbox plugin for vera
 * Copyright (C) 2014-2015  Eugenio "g7" Paolantonio and the Semplice Project
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

	public class Font : Object {
		/**
		 * Represents a Font.
		*/
		
		public string place { get; construct set; }
		
		public XmlNode node { get; construct set; }
		
		public string name {
			get {
				return node.get_child("name").content;
			}
			
			set {
				node.get_child("name").content = value;
			}
		}
		
		public int size {
			get {
				return int.parse(node.get_child("size").content);
			}
			
			set {
				node.get_child("size").content = value.to_string();
			}
		}
		
		public string weight {
			get {
				return node.get_child("weight").content;
			}
			
			set {
				node.get_child("weight").content = value;
			}
		}
		
		public string slant {
			get {
				return node.get_child("slant").content;
			}
			
			set {
				node.get_child("slant").content = value;
			}
		}
		
		private string _pretty; /* valac 0.26+ complains otherwise */
		public string pretty {
			get {
				_pretty = "%s%s%s %d".printf(
					name,
					(weight == "Normal") ? "" : " " + weight,
					(slant == "Normal") ? "" : " " + slant,
					size
				);
				
				return _pretty;
			}
			
			set {
				string[] split = value.split(" ");
								
				int new_size = -1;
				string new_slant = "Normal";
				string new_weight = "Normal";
				string new_font = "";
				for (int i=split.length-1; i >= 0; i--) {
					/* We loop in reverse */
					if (split[i] == "")
						continue;
					
					if (new_size == -1) {
						/* Size is always the first */
						new_size = int.parse(split[i]);
						continue;
					} else if (split[i].down() == "italic" || split[i].down() == "oblique") {
						/* Slant */
						new_slant = split[i];
						continue;
					} else if (split[i].down() == "bold") {
						/* Weight */
						new_weight = split[i];
						continue;
					}
					
					/* This *SHOULD* be the final font name */
					/* Vala doesn't support array slicing? Really? */
					for (int j=0; j <= i; j++) {
						new_font += (split[j] + ((j == i) ? "" : " "));
					}
					break;
				}
				
				this.size = new_size;
				this.slant = new_slant;
				this.weight = new_weight;
				this.name = new_font;
			}
		}
		
		public Font(string place, XmlNode node) {
			/**
			 * Constructor.
			*/
			
			this.place = place;
			this.node = node;
			
		}
		
	}
	
	public class OpenboxConfiguration : XmlFile {
		
		/**
		 * The OpenboxConfiguration class parses and handles the openbox
		 * configuration.
		*/
		
		const string[] SUPPORTED_FONT_PLACES = {
			"ActiveWindow",
			"InactiveWindow",
			"MenuHeader",
			"MenuItem",
			"OnScreenDisplay",
			"ActiveOnScreenDisplay",
			"InactiveOnScreenDisplay",
		};
		
		private Display display;
		private Settings settings;
		
		private XmlNode openbox_config;
		private XmlNode theme;
		
		private HashTable<string, Font> fonts = new HashTable<string, Font>(str_hash, str_equal);
		
		private void reconfigure_openbox() {
			/**
			 * Tells openbox to reload the configuration.
			*/
			
			try {
				Process.spawn_command_line_sync("openbox --reconfigure");
			} catch (SpawnError e) {
				warning("ERROR: Unable to reconfigure openbox: %s\n", e.message);
			}
			
		}
		
		private void on_settings_changed(string key) {
			/**
			 * Fired when a setting has been changed.
			*/
			
			if (key == "desktops-number") {
				this.display.change_desktops_number(this.settings.get_int(key));
			} else if (key.has_prefix("font-")) {
				this.fonts[key.replace("font-","")].pretty = this.settings.get_string(key);
			}
						
			this.write();
			
			if (key != "desktops-number")
				this.reconfigure_openbox();
		}
				
		public OpenboxConfiguration(Display display, Settings settings, string file_path) {
			/**
			 * Constructor.
			*/

			base(file_path);
			
			this.display = display;
			this.settings = settings;

			/* Obtain nodes for the items we expose via dconf */
			this.openbox_config = this.root_node.get_child("openbox_config");
			this.theme = this.openbox_config.get_child("theme");
			
			/* Bind dconf to xml */
			
			/* theme-name */
			this.settings.bind(
				"theme-name",
				this.theme.get_child("name"),
				"content",
				SettingsBindFlags.DEFAULT
			);
			
			/* desktops-number */
			this.settings.bind_with_mapping(
				"desktops-number",
				this.openbox_config.get_child("desktops").get_child("number"),
				"content",
				SettingsBindFlags.DEFAULT,
				(v, a) => {
					try {
						v.set_string(a.get_int32().to_string());
						return true;
					} catch (Error e) {
						return false;
					}
				},
				(v, t) => {
					return new Variant.int32(int.parse(v.get_string()));
				},
				null,
				null
			);
			
			/* title-layout */
			this.settings.bind(
				"title-layout",
				this.theme.get_child("titleLayout"),
				"content",
				SettingsBindFlags.DEFAULT
			);
			
			/* Fonts */
			string place;
			Font font;
			foreach (XmlNode node in this.theme.get_childs("font")) {
				place = node.attributes.get("place");
				
				if (likely(place in SUPPORTED_FONT_PLACES)) {
					font = new Font(place, node);
					//font.pretty = this.settings.get_string("font-%s".printf(place.down()));
					this.fonts.set(place.down(), font);
					
					/* FIXME: binding doesn't seem to work fully */
					/*this.settings.bind(
						"font-%s".printf(place.down()),
						font,
						"pretty",
						SettingsBindFlags.DEFAULT
					);
					*/
					
				}
			}
			
			/* Subscribe to settings change */
			this.settings.changed.connect(this.on_settings_changed);
			
		}
		
	}

}

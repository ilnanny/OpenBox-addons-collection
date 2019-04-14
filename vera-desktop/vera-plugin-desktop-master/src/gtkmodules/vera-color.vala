/*
 * vera-plugin-desktop - desktop plugin for vera
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

public class VeraColor : Object {

	private static Settings settings;
	private static Gtk.CssProvider provider;
	
	private static void reset_widgets() {
		/**
		 * Repaints the widgets.
		*/
		
		Idle.add(
			() => {
				Gtk.StyleContext.reset_widgets(Gdk.Screen.get_default());
				return false;
			}
		);
	}
	
	private static void on_vera_color_enabled_changed() {
		/**
		 * Fired when the 'vera-color-enabled' property has been changed.
		*/
				
		if (settings.get_boolean("vera-color-enabled")) {
			Gtk.StyleContext.add_provider_for_screen(
				Gdk.Screen.get_default(),
				provider,
				Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS
			);
			
			on_vera_color_changed();
		} else {
			Gtk.StyleContext.remove_provider_for_screen(
				Gdk.Screen.get_default(),
				provider
			);

			reset_widgets();
		}
		
	}
	
	private static void on_vera_color_changed() {
		/**
		 * Fired when the 'vera-color' property has been changed.
		*/
		
		if (!settings.get_boolean("vera-color-enabled"))
			return;
		
		provider.load_from_data(
			"@define-color vera-color %s;".printf(settings.get_string("vera-color")),
			-1
		);
		
		reset_widgets();
		
	}
	
	[CCode (cname = "g_module_check_init")]
	public static string? g_module_load(Module module) {
		/**
		 * Pre-initialization.
		*/
		
		/* Ensure that the module stays resident */
		module.make_resident();
		
		return null;
	}
	
	[CCode (cname = "gtk_module_init")]
	public static void gtk_module_init(int argc, string[] argv) {
		/**
		 * Initializes the module.
		*/
		
		provider = new Gtk.CssProvider();
		
		settings = new Settings("org.semplicelinux.vera.desktop");
		settings.changed["vera-color-enabled"].connect(on_vera_color_enabled_changed);
		settings.changed["vera-color"].connect(on_vera_color_changed);
		
		on_vera_color_enabled_changed();
		
	}

}

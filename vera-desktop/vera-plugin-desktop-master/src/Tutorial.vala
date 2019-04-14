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

using Vera;

namespace DesktopPlugin {
		
	public class TutorialPage : Gtk.Box {
		
		/**
		 * This class represents a page of the Tutorial.
		 * It's a Gtk.Box which contains a label and some other
		 * (optional) things.
		*/
		
		private Gtk.Label text_content;
		
		public TutorialPage(string content, Pango.AttrList attributes) {
			/**
			 * Constructs the object.
			*/
			
			Object(orientation: Gtk.Orientation.VERTICAL);
			this.get_style_context().add_class("tutorial-page");
			
			// Create the text_content
			this.text_content = new Gtk.Label(null);
			this.text_content.attributes = attributes;
			this.text_content.set_markup(content);
			this.text_content.set_line_wrap(true);
			this.text_content.set_line_wrap_mode(Pango.WrapMode.WORD);
			this.text_content.set_justify(Gtk.Justification.CENTER);
			
			this.text_content.set_margin_top(20);
			this.text_content.set_margin_bottom(20);
			
			Gdk.RGBA color = Gdk.RGBA();
			color.parse("#13135E");
			
			Gdk.RGBA foreground = Gdk.RGBA();
			foreground.parse("#fff");
			//this.override_background_color(Gtk.StateFlags.NORMAL, color);
			//this.override_foreground_color(Gtk.StateFlags.NORMAL, foreground);
			
			this.pack_start(this.text_content, true, true, 0);
			
			this.valign = Gtk.Align.CENTER;
			
			this.show_all();
		}
	
	}

	public class Tutorial : Gtk.Stack {
		
		/**
		 * The Tutorial class is a widget based on Gtk.Stack that
		 * provides some nice pointers to the user to get started
		 * with Vera.
		*/
		
		private Pango.AttrList tutorial_label_attributes;
		
		private Pango.Attribute weight;
		private Pango.Attribute font;
		private Pango.Attribute foreground_color;
		private Pango.FontDescription font_desc;
		
		public Tutorial() {
			/**
			 * Constructs the object.
			*/
						
			Object();
			this.set_transition_type(Gtk.StackTransitionType.SLIDE_DOWN);
			this.set_transition_duration(800);

			this.name = "tutorial";
			
			// Build TutorialLabelAttributes
			this.tutorial_label_attributes = new Pango.AttrList();
			
			this.weight = Pango.attr_weight_new(Pango.Weight.LIGHT);
			
			this.font_desc = Pango.FontDescription.from_string("Open Sans, , 45px");
			this.font = new Pango.AttrFontDesc(this.font_desc);
			
			this.foreground_color = Pango.attr_foreground_new(65535, 65535, 65535);
						
			this.tutorial_label_attributes.insert((owned)this.font);
			this.tutorial_label_attributes.insert((owned)this.weight);
			this.tutorial_label_attributes.insert((owned)this.foreground_color);
			
			/*
			 * Initial message, that prompts the user to right-click
			 * anywhere in the desktop.
			*/
			//"Per iniziare, fai clic con il tasto destro in un punto qualsiasi.",
			this.add_named(
				new TutorialPage(
					_("To start, right-click anywhere in the desktop."),
					this.tutorial_label_attributes
				),
				"menu"
			);
			
			/*
			 * This message shows up after right-clicking. We explain what
			 * the user has just done, and prompt it to write something,
			 * so we'll show up the launcher.
			*/
			//"Fantastico! Hai appena aperto il menù principale di Semplice.\nAdesso scrivi qualcosa sulla tastiera.",
			this.add_named(
				new TutorialPage(
					_("Great! You have just opened the main Semplice menu.\nNow write something in the keyboard."),
					this.tutorial_label_attributes
				),
				"launcher"
			);
			
			/*
			 * We'll show the following message when the launcher has been
			 * expanded.
			*/
			//"Da qui puoi facilmente aprire nuove applicazioni.\nPremi Esc per nascondere il launcher.",
			this.add_named(
				new TutorialPage(
					_("From here you can easily open new applications.\nPress Esc to hide the launcher."),
					this.tutorial_label_attributes
				),
				"close_launcher"
			);
			
			/*
			 * The end!
			*/
			//"Adesso puoi utilizzare Semplice. Divertiti!",
			this.add_named(
				new TutorialPage(
					_("Now you can use Semplice. Enjoy!"),
					this.tutorial_label_attributes
				),
				"end"
			);
			
			/*
			 * Blank
			*/
			this.add_named(
				new Gtk.Fixed(),
				"blank"
			);
			
			
			this.show_all();
		}
		
		~Tutorial() {
			/**
			 * Deconstructor.
			*/
			
			this.weight.destroy();
			this.foreground_color.destroy();
		}
		
	}


}

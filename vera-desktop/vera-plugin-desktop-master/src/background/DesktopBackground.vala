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
    
    public enum BackgroundMode {
        COLOR = 1,
        TILE = 2,
        STRETCH = 3,
        SCREEN = 4,
        FIT = 5,
        CROP = 6,
        CENTER = 7;
    }
    
	public class DesktopBackground : Gtk.EventBox {

		/**
		 * The DesktopBackground widget. This is the main part of
		 * DesktopPlugin.
		 */
         
        private XlibDisplay xlib_display;
        
        private int monitor_number;

        private DesktopWindow parent_window;

        private bool painted = false;

        private Settings settings;
        
        public signal void menu_shown ();
        
        /* Background */
        private Gdk.RGBA background_color = Gdk.RGBA();
        private weak Gdk.Pixbuf current_background;
        private BackgroundMode current_background_mode {
            get {
                return (BackgroundMode)this.settings.get_enum("background-mode");
            }
        }

        private bool on_button_pressed(Gdk.EventButton evnt) {
                        
            if (evnt.button == Gdk.BUTTON_PRIMARY) {
                /* If primary button (usually left), we need to regain focus */
                this.parent_window.set_focus(this);
            } else {
                /* Otherwise, forward the event to the root window (if we are on X) */
                
                if (evnt.button == Gdk.BUTTON_SECONDARY) {
                    /* That's probably the WM menu */
                    this.menu_shown();
                }
                
                this.xlib_display.send_to_root_window(evnt);
            }

            return true;
        }
        
        public void load_background(Cairo.XlibSurface xlib_surface, Gdk.Pixbuf? pixbuf = null) {
            /**
             * Loads the background.
            */

            Gdk.Rectangle geometry;
            BackgroundMode mode = (pixbuf != null) ? this.current_background_mode : BackgroundMode.COLOR;
            Gdk.Screen scr = this.parent_window.get_screen();

            /* Abort if monitor is offline */
            if (this.monitor_number >= scr.get_n_monitors()) {
                warning("Monitor %d offline, skipping...", this.monitor_number);
                return;
            }
            
            /* Create a subsurface of the current monitor size */
            scr.get_monitor_geometry(this.monitor_number, out geometry);
            Cairo.Surface surface = new Cairo.Surface.for_rectangle(
                xlib_surface,
                geometry.x,
                geometry.y,
                geometry.width,
                geometry.height
            );
            
            /* ...and the relative Context */
            Cairo.Context context = new Cairo.Context(surface);

            string color = this.settings.get_string("background-color");
            if (!this.background_color.parse(color)) {
                /* Color has not been parsed correctly */
                warning("Unable to parse background color, skipping...");
                return;
            }
            
            BackgroundInfo? infos = BackgroundTools.get_background_info(mode, geometry, pixbuf);
            switch (mode) {
                
                case BackgroundMode.COLOR:
                    /*
                     * Colors!
                    */
                                        
                    BackgroundTools.color(context, this.background_color);
                    break;
                
                case BackgroundMode.TILE:
                    /*
                     * Tile
                    */
                                        
                    if (pixbuf.has_alpha)
                        BackgroundTools.color(context, this.background_color);
                    
                    BackgroundTools.tile(infos, context, pixbuf);
                    break;
                
                case BackgroundMode.STRETCH:
                    /*
                     * Stretch
                    */
                                        
                    if (pixbuf.has_alpha)
                        BackgroundTools.color(context, this.background_color);
                    
                    BackgroundTools.stretch(infos, context, pixbuf);
                    break;
                
                case BackgroundMode.SCREEN:
                    /*
                     * Screen
                    */
                                        
                    if (pixbuf.has_alpha)
                        BackgroundTools.color(context, this.background_color);
                    
                    BackgroundTools.general(infos, context, pixbuf);
                    break;
                
                case BackgroundMode.CROP:
                    /*
                     * Crop
                    */
                                        
                    if (pixbuf.has_alpha)
                        BackgroundTools.color(context, this.background_color);
                    
                    BackgroundTools.crop(infos, context, pixbuf);
                    break;

                case BackgroundMode.FIT:
                    /*
                     * Fit
                    */
                                        
                    BackgroundTools.color(context, this.background_color);
                    
                    BackgroundTools.fit(infos, context, pixbuf);
                    break;
                
                case BackgroundMode.CENTER:
                    /*
                     * Center
                    */
                                        
                    BackgroundTools.color(context, this.background_color);
                    
                    BackgroundTools.general(infos, context, pixbuf);
                    break;
                    
            }
            
            /* Set background */
            Cairo.Pattern pattern = new Cairo.Pattern.for_surface(surface);
            /*
             * FIXME: GTK+ 3.20 broke the EventBox painting.
             * As a workaround, paint on the parent window instead.
             * Unfortunately, this doesn't permit to have the "slide down"
             * animation as the EventBox will be empty
            */
            //this.get_window().set_background_pattern(pattern);
            this.parent_window.get_window().set_background_pattern(pattern);
            this.parent_window.queue_draw();
            //X.free_pixmap(this.xlib_display.display, xpixmap);
            
        }
                    

		public DesktopBackground(DesktopWindow parent_window, Settings settings, int monitor_number) {
            /**
             * Constructs the DesktopBackground.
             */

            Object();
            
            /* Monitor number */
            this.monitor_number = monitor_number;
            
            /* Events */
            this.add_events(
                Gdk.EventMask.BUTTON_PRESS_MASK |
                Gdk.EventMask.BUTTON_RELEASE_MASK |
                Gdk.EventMask.KEY_PRESS_MASK |
                Gdk.EventMask.KEY_RELEASE_MASK |
                Gdk.EventMask.ENTER_NOTIFY_MASK |
                Gdk.EventMask.LEAVE_NOTIFY_MASK
            );
            this.can_focus = true;

            this.parent_window = parent_window;
            
            /* Xlibdisplay? */
            this.xlib_display = (XlibDisplay)this.parent_window.display;

            this.settings = settings;
            
            this.set_app_paintable(true);

            this.button_press_event.connect(this.on_button_pressed);
            
            /*
            this.realize.connect(
                (widget) => {
                    this.load_background();
                }
            );
            */


		}

	}

}

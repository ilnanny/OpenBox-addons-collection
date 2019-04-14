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

    public class DesktopWindow : Gtk.Window {

	/**
	 * A DesktopWindow is a Window ready for our
	 * use.
	*/

	public bool launcher_enabled { get; construct set; }

	public DesktopBackground desktop_background { get; private set; }
	public DesktopLauncher desktop_launcher { get; private set; }

	public Gdk.Rectangle screen_size;
        private Gdk.Screen default_screen;
        private Gdk.Window root_window;

        public Display display;
        private Settings settings;
	private Gtk.Box container;
	
	private GMenuLoader gmenu_loader;
	
	public Tutorial tutorial;
	private ulong tutorial_menu;
	private ulong tutorial_launcher_opened;
	private ulong tutorial_launcher_closed;
	
	public signal void size_changed();

        public void stack_switch(string name) {
            /**
            Switches the Gtk.Stack to the given name.
            */

	    return;
            //this.stack.set_visible_child_name(name);
        }
	
	private void on_launcher_closed() {
	    
	    this.desktop_background.grab_focus();
	
	}

        public void show_tutorial() {
            /**
             * Creates and shows the Tutorial.
             * The object will be stored in this.tutorial.
            */
            	    
            this.tutorial = new Tutorial();
            this.desktop_background.add(this.tutorial);
        }
	
	private void tutorial_on_menu_shown() {
	    /**
	     * Fired when the menu has been shown (and we may
	     * switch to the next tutorial item if we should)
	    */
	    
	    if (this.tutorial.visible_child_name == "menu") {
		/* We can go ahead */
		if (this.launcher_enabled)
		    this.tutorial.set_visible_child_name("launcher");
		else
		    /* Force the end as the launcher is disabled */
		    this.tutorial_on_launcher_closed();
	    }
	}
	
	private void tutorial_on_launcher_opened() {
	    /**
	     * Fired when the launcher has been shown (triggered by
	     * a key-press).
	    */
	    
	    if (this.tutorial.visible_child_name == "launcher") {
		/* We can go ahead */
		this.tutorial.set_visible_child_name("close_launcher");
	    }
	    
	}
	
	private void tutorial_on_launcher_closed() {
	    /**
	     * Fired when the launcher has been closed
	    */
	    
	    if (
		this.tutorial.visible_child_name == "close_launcher" ||
		(!this.launcher_enabled && this.tutorial.visible_child_name == "menu")
	    ) {
		/* We can go ahead */
		Timeout.add_seconds(1,
		    /* We delay here to take in account the launcher animation */
		    () => {
			this.tutorial.set_visible_child_name("end");
			
			return false; /* remove */
		    }
		);
	    
		/* Nice animation after 10 seconds */
		Timeout.add_seconds(11,
		    () => {
			this.tutorial.set_visible_child_name("blank");
			
			return false; // remove
		    }
		);
		
		/* After 11 seconds, we can safely destroy the tutorial. */
		Timeout.add_seconds(12,
		    () => {
			this.tutorial.destroy();
			
			return false; // remove
		    }
		);
		
		/* Also disconnect everything */
		this.disconnect_for_tutorial();
		
		/* Finally, disabling the tutorial for the next time... */
		if (!this.settings.set_boolean("show-tutorial", false)) {
		    warning("Something wrong occurred when disabling the tutorial.");
		}
	    }
	    
	}
	
	public void connect_for_tutorial() {
	    /**
	     * Connects things up so that we are able to do neat
	     * things for the tutorial.
	    */
	    	    
	    this.tutorial_menu =
		this.desktop_background.menu_shown.connect(this.tutorial_on_menu_shown);
	    if (this.launcher_enabled) {
		this.tutorial_launcher_opened =
		    this.desktop_launcher.launcher_opened.connect(this.tutorial_on_launcher_opened);
		this.tutorial_launcher_closed =
		    this.desktop_launcher.launcher_closed.connect(this.tutorial_on_launcher_closed);
	    }
	    
	}
	
	private void disconnect_for_tutorial() {
	    /**
	     * The inverse of this.connect_for_tutorial().
	    */
	    
	    this.desktop_background.disconnect(this.tutorial_menu);
	    if (this.launcher_enabled) {
		this.desktop_launcher.disconnect(this.tutorial_launcher_opened);
		this.desktop_launcher.disconnect(this.tutorial_launcher_closed);
	    }
	    
	}
	
	public void resize_window(Gdk.Rectangle new_size, bool move_only = false) {
	    /**
	     * Resizes the window with the given new size.
	    */
	    
	    /* The monitor coordinates may have changed, restore position */
	    this.move(new_size.x, new_size.y);

	    /* Store changes */
	    this.screen_size.x = new_size.x;
	    this.screen_size.y = new_size.y;
	    this.screen_size.height = new_size.height;
	    this.screen_size.width = new_size.width;
	    
	    /* Finally, resize and tell listeners about it */
	    if (!move_only) {
		this.resize(new_size.width, new_size.height);
		this.size_changed();
	    }
	}
		

	public DesktopWindow(Gdk.Rectangle screen_size, Settings settings, GMenuLoader gmenu_loader, Display display, int monitor_number) {
	    /**
	     * Constructs the DesktopWindow.
	    */

	    Object();

	    /* Set as paintable */
	    this.set_app_paintable(true);

	    /* Get screen and root window */
            //this.screen = Gdk.Screen.get_default();
            this.root_window = Gdk.get_default_root_window();

	    this.screen_size = screen_size;
	    
            this.settings = settings;
	    
	    this.gmenu_loader = gmenu_loader;
            
            this.display = display;

            this.type_hint = Gdk.WindowTypeHint.DESKTOP;
            this.set_keep_below(true);
	    
	    /* Launcher enabled? */
	    this.launcher_enabled = this.settings.get_boolean("show-launcher");

            /* Move and resize window */
            this.move(this.screen_size.x, this.screen_size.y);
            this.resize(this.screen_size.width, this.screen_size.height);

	    /* Create the container */
	    this.container = new Gtk.Box(Gtk.Orientation.VERTICAL, 0);
	    this.add(this.container);

	    /* Instantiate the background widget */
	    this.desktop_background = new DesktopBackground(this, settings, monitor_number);

	    /* Instantiate, pack and connect the launcher widget */
	    if (this.launcher_enabled) {
		this.desktop_launcher = new DesktopLauncher(this, settings, gmenu_loader);
		this.container.pack_start(this.desktop_launcher, false, false, 0);
		
		this.desktop_launcher.launcher_closed.connect(this.on_launcher_closed);
		this.desktop_background.key_press_event.connect(this.desktop_launcher.open_launcher);
	    }
	    
	    /* Finally pack the background widget */
	    this.container.pack_start(this.desktop_background, true, true, 0);
	    
	}

    }

}

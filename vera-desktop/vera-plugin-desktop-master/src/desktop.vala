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

const string GETTEXT_PACKAGE = "vera-plugin-desktop";

namespace DesktopPlugin {
    
    extern void set_x_property(X.Display display, X.Window window, X.Atom atom, X.Pixmap pixmap);

    public const string SUPPORTED_MIMETYPES[] = {
	"image/bmp",
	"image/gif",
	"image/jpeg",
	"image/x-portable-bitmap",
	"image/png",
	"image/xbm"
    };

    public class Plugin : Peas.ExtensionBase, VeraPlugin {

	private GMenuLoader gmenu_loader;

	public Display display;
	private XlibDisplay? xlib_display = null;

	public Settings settings;
	private DesktopWindow[] window_list = new DesktopWindow[0];
	
	private X.Pixmap? xpixmap = null;
	private Cairo.XlibSurface xlib_surface;
	
	private uint background_random_timeout = 0;
	
	private int monitor_number;
	private int realized_backgrounds = 0;
	
	private bool tutorial_enabled;
		
	private void on_settings_changed(string key) {
	    /**
	     * Fired when the settings of vera-desktop have been changed.
	     * Currently we handle only the wallpaper so we'll invoke
	     * update_background().
	    */
	    
	    switch (key) {
		
		case "vera-color-lock":
		    if (!this.settings.get_boolean("vera-color-lock"))
			/*
			 * vera-color-lock just disabled, we need to recalculate
			 * the average color...
			*/
			this.set_average_from_current_wallpaper();
		    
		    break;
		
		case "background-random-timeout":
		case "background-random-enabled":
		    if (this.settings.get_boolean("background-random-enabled"))
			this.create_random_timeout();
		    else
			this.remove_random_timeout();
		    
		    break;
		
		case "background-color":
		case "image-path":
		case "background-mode":
		    this.update_background(true);
		    if (this.settings.get_boolean("background-random-enabled"))
			this.reset_random_timeout();
		    
		    break;
		    
	    }
	    
	}
	
	private string get_average_from_pixbuf(Gdk.Pixbuf pixbuf) {
	    /**
	     * Returns a processed average color from the given pixbuf.
	    */
	    
	    Gdk.RGBA average_color = AverageColor.pixbuf_average_RGBA(pixbuf);
	    double luma = (0.2126 * average_color.red + 0.7152 * average_color.green + 0.0722 * average_color.blue);
	    
	    if (luma > 0.5) {
		/* Too bright */
		luma -= 0.5;
		
		average_color.red -= luma*average_color.red;
		average_color.blue -= luma*average_color.blue;
		average_color.green -= luma*average_color.green;
	    }
	    
	    return average_color.to_string();
	    
	}
	
	private void set_average_from_current_wallpaper() {
	    /**
	     * Sets the average color from the current wallpaper.
	    */
	    
	    if (!this.settings.get_boolean("vera-color-enabled"))
		/* Disabled, bye */
		return;
	    
	    string wallpaper = this.settings.get_strv("image-path")[0];
	    
	    try {
		this.settings.set_string(
		    "vera-color",
		    this.get_average_from_pixbuf(
			new Gdk.Pixbuf.from_file(wallpaper)
		    )
		);
	    } catch (Error e) {}
	    
	}
	
	private void update_background(bool set_vera_color = false) {
	    /**
	     * Updates the background.
	    */
	    
	    Gdk.Screen scr = this.window_list[0].get_screen();
            weak X.Screen xscreen = X.Screen.get_screen(this.xlib_display.display, scr.get_number());
	    
	    if (this.xpixmap != null)
		X.free_pixmap(this.xlib_display.display, this.xpixmap);

            /* Create X Pixmap */
            this.xpixmap = X.CreatePixmap(
                this.xlib_display.display,
                this.xlib_display.xrootwindow,
                scr.get_width(),
                scr.get_height(),
                xscreen.default_depth_of_screen()
            );
                        
            /* Create Cairo Surface */
            this.xlib_surface = new Cairo.XlibSurface(
                this.xlib_display.display,
                (int)this.xpixmap,
                Gdk.X11Visual.get_xvisual(scr.get_system_visual()),
                scr.get_width(),
                scr.get_height()
            );
	    
	    string[] backgrounds = this.settings.get_strv("image-path");
	    BackgroundMode type = (BackgroundMode)this.settings.get_enum("background-mode");
	    
	    if (backgrounds.length == 0 && type != BackgroundMode.COLOR) {
		/* Empty background list, bye */
		return;
	    }
	    
	    /* Loop through the monitors */
	    DesktopBackground background_object;
	    Gdk.Pixbuf pixbuf = null;
	    string path;
	    for (int i = 0; i < this.window_list.length; i++) {
		
		background_object = this.window_list[i].desktop_background;
		
		/*
		 * We should now select the background to paint.
		 * The 'image-path' configuration property in the
		 * gsettings schema is a string array, that contains
		 * (in the correct order) the image to set for every
		 * monitor.
		 * When a monitor doesn't have its specified wallpaper,
		 * we will fallback to the first.
		 * 
		 * Another exception is when the background-mode is
		 * SCREEN: we will pick only the first wallpaper.
		*/
		
		if ((i < backgrounds.length && backgrounds[i] != "") && type != BackgroundMode.SCREEN) {
		    path = backgrounds[i];
		} else {
		    path = backgrounds[0];
		}
		
		if (path == "" && type != BackgroundMode.COLOR) {
		    /* Safety check */
		    continue;
		}

		if (type != BackgroundMode.COLOR && !(type == BackgroundMode.SCREEN && i > 0)) {
		    /* If the mode is SCREEN and this isn't the first
		     * monitor, we already have the pixbuf... */
			
		    pixbuf = new Gdk.Pixbuf.from_file(path);

		    if (set_vera_color && i == 0) {
			/* If this is the first monitor, obtain the
			 * dominant color if we should */

			if (!this.settings.get_boolean("vera-color-lock") &&
			    this.settings.get_boolean("vera-color-enabled"))
			{
			    this.settings.set_string(
				"vera-color",
				this.get_average_from_pixbuf(pixbuf)
			    );
			}
		    }

		    if (type == BackgroundMode.SCREEN) {
			/* Scale the image if we should */
			int screen_width = scr.get_width();
			int screen_height = scr.get_height();
			
			if (!(screen_width == pixbuf.get_width() && screen_height == pixbuf.get_height())) {
			    pixbuf = pixbuf.scale_simple(
				screen_width,
				screen_height,
				Gdk.InterpType.BILINEAR
			    );
			}
		    }
		}
		
		background_object.load_background(this.xlib_surface, pixbuf);
	    }

	    /*
	     * Now we need to set the root map on X.
	     * This is needed because when we lack of true transparency
	     * (i.e. we do not have a composite WM active) many applications
	     * (such as tint2, xchat, many terminals, etc) rely on
	     * the _XROOTPMAP_ID atom to create a fake transparency.
	     * 
	     * The specification talk also about the ESETROOT_PMAP_ID property,
	     * but as we are a permanent (hopefully) client, we aren't going
	     * to set it.
	     * The PCManFM guys did the same (and I use this space to thank
	     * them, most code in this source file is inspired by PCManFM's
	     * desktop.c).
	    */
	    
	    this.xlib_display.display.grab_server();
	    
	    X.Atom atm = this.xlib_display.display.intern_atom("_XROOTPMAP_ID", false);
	    /*
	     * I'm sorry.
	     * Yes, I'm serious.
	     * 
	     * set_x_property() is nothing but an external C function
	     * located in workarounds/xsetproperty.c.
	     * 
	     * Unfortunately, Vala's X.Display.change_property(), does not
	     * work as it should, and we end up with nothing set as
	     * _XROOTPMAP_ID in the best case, and with a fucked X in the
	     * worst (bad Pixmap and some applications that rely on that
	     * property may crash, it happened to me with xchat).
	     * 
	     * I hope to use a Vala equivalent when possible, in the mean
	     * time, please accept this workaround.
	    */
	    set_x_property(this.xlib_display.display, this.xlib_display.xrootwindow, atm, this.xpixmap);
	    
	    /* SetWindowBackgroundPixmap is required for conky transparency */
	    X.SetWindowBackgroundPixmap(this.xlib_display.display, this.xlib_display.xrootwindow, (int)xpixmap);
	    
	    X.ClearWindow(this.xlib_display.display, this.xlib_display.xrootwindow);
	    this.xlib_display.display.flush();
	    this.xlib_display.display.ungrab_server();

	}
	
	private string[] enumerate_wallpapers(string? given_path = null) {
	    /**
	     * Returns a list of wallpapers.
	    */
	    
	    string[] wallpapers = new string[0];
	    
	    string[] excluded = this.settings.get_strv("background-exclude");
	    string[] paths;
	    if (given_path != null) {
		paths = new string[1] { given_path };
	    } else {
		paths = this.settings.get_strv("background-search-paths");
	    }
	    
	    File file;
	    FileInfo info;
	    FileEnumerator enumerator;
	    string full_path;
	    foreach (string path in paths) {
		try {
		    file = File.new_for_path(path);
		    enumerator = file.enumerate_children(
			(
			    FileAttribute.STANDARD_NAME + "," +
			    FileAttribute.STANDARD_TYPE + "," +
			    FileAttribute.STANDARD_CONTENT_TYPE
			),
			FileQueryInfoFlags.NONE,
			null
		    );
		    
		    info = null;
		    while ((info = enumerator.next_file(null)) != null) {
			full_path = file.resolve_relative_path(info.get_name()).get_path();
			if (info.get_file_type() == FileType.DIRECTORY) {
			    foreach (string _path in this.enumerate_wallpapers(full_path)) {
				wallpapers += _path;
			    }
			} else {
			    if (info.get_content_type() in SUPPORTED_MIMETYPES && !(full_path in excluded)) {
				wallpapers += full_path;
			    }
			}
		    }
		} catch (Error e) {
		    warning("Error while enumerating wallpapers: %s", e.message);
		}
	    }
	    
	    if (given_path == null) {
		/* Also add the manually included wallpapers */
		foreach (string path in this.settings.get_strv("background-include")) {
		    if (FileUtils.test(path, FileTest.EXISTS)) {
			wallpapers += path;
		    }
		}
	    }
	    
	    return wallpapers;
	}
	
	private bool on_random_timeout_elapsed() {
	    /**
	     * Fired when the Random timeout has been elapsed.
	    */
	    	    
	    Idle.add(
		() => {
		    
		    string[] wallpapers = this.enumerate_wallpapers();
		    if (wallpapers.length > 0) {
			string random = wallpapers[Random.int_range(0, wallpapers.length-1)];
			
			this.settings.set_strv("image-path", { random });
		    }
		    
		    
		    return false;
		}
	    );
	    
	    return true;
	}
	
	private void create_random_timeout() {
	    /**
	     * Creates the random timeout.
	    */
	    
	    if (this.background_random_timeout > 0)
		this.remove_random_timeout();
	    	    
	    this.background_random_timeout = Timeout.add_seconds(
		this.settings.get_int("background-random-timeout") * 60,
		this.on_random_timeout_elapsed
	    );
	}
	
	private void remove_random_timeout() {
	    /**
	     * Removes the random timeout.
	    */
	    
	    if (this.background_random_timeout == 0)
		return;
	    	    
	    Source.remove(this.background_random_timeout);
	    this.background_random_timeout = 0;
	}
	
	private void reset_random_timeout() {
	    /**
	     * Resets the random timeout.
	     * 
	     * This is the equivalent of calling remove_random_timeout()
	     * and create_random_timeout().
	    */
	    
	    this.remove_random_timeout();
	    this.create_random_timeout();
	}
	
	private void on_desktopbackground_realized(Gtk.Widget desktop_background) {
	    /**
	     * We use this method to track down the realized DesktopBackgrounds.
	     * We will draw the background once all the DesktopBackgrounds are realized.
	    */
	    
	    this.realized_backgrounds++;
	    
	    if (this.realized_backgrounds == this.monitor_number) {
		/* We can draw the background */
		
		if (this.settings.get_boolean("background-random-enabled")) {
		    this.on_random_timeout_elapsed();
		    this.create_random_timeout();
		} else {
		    this.update_background();
		}
		
		/* Finally reset normal background color */
		foreach (DesktopWindow window in this.window_list) {
		    window.get_style_context().remove_class("initialization");
		}
	    }
	}
	
	private void on_monitors_changed() {
	    /**
	     * Fired when the active monitor number changed.
	    */
	    
	    Gdk.Screen screen = Gdk.Screen.get_default();
	    int current_monitor_number = screen.get_n_monitors();
	    
	    if (current_monitor_number == this.monitor_number) {
		/* The monitor number didn't change, skipping */
		return;
	    } else if (current_monitor_number < this.monitor_number) {
		/*
		 * FIXME: Currently disconnected monitors will have their
		 * desktop window unfreed. That's because we can't - currently -
		 * reliably determine which monitor got disconnected and, to
		 * avoid nasty things happen (such as destroying the wrong window),
		 * the disconnected monitor's window will remain open.
		 * 
		 * This is obviously a bug and should be fixed.
		*/
		
		return;
	    } else {
		/* New monitor */
		this.populate_screens(current_monitor_number-1);
	    }
		
	    this.monitor_number = current_monitor_number;
	    
	}
	
	private void on_size_changed() {
	    /**
	     * Fired when the size of a monitor changed.
	    */
	    
	    Gdk.Screen screen = Gdk.Screen.get_default();
	    
	    bool changed = false;
	    DesktopWindow window;
	    Gdk.Rectangle rectangle;
	    for (int i = 0; i < this.window_list.length; i++) {
		window = this.window_list[i];

		/* Abort if monitor is not meant to be */
		if (i >= this.monitor_number) {
		    break;
		}
		
		/* Get new screen geometry */
		screen.get_monitor_geometry(i, out rectangle);
		
		if (rectangle.height != window.screen_size.height || rectangle.width != window.screen_size.width) {
		    /* Something changed, resize the DesktopWindow */
		    changed = true;
		    window.resize_window(rectangle);
		} else if (rectangle.x != window.screen_size.x || rectangle.y != window.screen_size.y) {
		    /* Move only */
		    window.resize_window(rectangle, true);
		}
	    }
	    
	    /* This is pretty ignorant, but should be enough for the time being */
	    if (changed)
		this.update_background();
	}
	    

	private void populate_screens(int process_only_one = -1) {
	    /**
	     * This is the method that will create and position the DesktopWindows
	     * on every monitor of the computer.
	    */

	    Gdk.Screen screen = Gdk.Screen.get_default();
	    Gdk.Rectangle rectangle;
	    DesktopWindow window;
	    
	    /* Is the tutorial enabled? */
	    this.tutorial_enabled = this.settings.get_boolean("show-tutorial");
	    
	    /* Set monitor number */
	    this.monitor_number = screen.get_n_monitors();

	    for (int i = ((process_only_one == -1) ? 0 : process_only_one); i < this.monitor_number; i++) {
		/* Loop through the monitors found */
		
		/* Get Rectangle of the monitor */
		screen.get_monitor_geometry(i, out rectangle);
		
		/* Create window */
		window = new DesktopWindow(rectangle, this.settings, this.gmenu_loader, this.display, i);
		this.window_list += window;

		/* Make the background black before rendering the wallpapers */
		window.get_style_context().add_class("initialization");
		
		window.desktop_background.realize.connect(this.on_desktopbackground_realized);
		window.show_all();
		
		/* If the tutorial is enabled, we need to connect things up */
		if (this.tutorial_enabled)
		    window.connect_for_tutorial();
		
		if (process_only_one > -1)
		    /* Done */
		    return; /* FIXME: Should look at this more closely */

	    }
	    
	    /*
	     * We now do something only on the first window:
	     *  - We will 'present' it, so it becomes fully focused
	     *    and ready to listen to keystrokes
	     *  - We will show the Tutorial if the configuration says so.
	    */
	    
	    if (this.tutorial_enabled) {
		/* Yes, we need to show tutorial. */
		this.window_list[0].show_tutorial();
		
		/*
		 * As we run the tutorial only on the first monitor, we need
		 * to share our Tutorial object with the other ones...
		*/
		for (int i=1; i < this.window_list.length; i++) {
		    this.window_list[i].tutorial = this.window_list[0].tutorial;
		}
	    }
	    
	    this.window_list[0].present();
	}

	public void init(Display display) {
	    /**
	     * Initializes the plugin.
	    */
	    
	    /* Translations */
	    Intl.setlocale(LocaleCategory.MESSAGES, "");
	    Intl.textdomain(GETTEXT_PACKAGE); 
	    Intl.bind_textdomain_codeset(GETTEXT_PACKAGE, "utf-8"); 
	    
	    try {
		this.display = display;
		this.xlib_display = (XlibDisplay)display;
		    
		this.settings = new Settings("org.semplicelinux.vera.desktop");

		this.settings.changed.connect(this.on_settings_changed);

	    } catch (Error ex) {
		error("Unable to load plugin settings.");
	    }
	    
	    /* React to Gdk.Screen's monitors_changed */
	    Gdk.Screen screen = Gdk.Screen.get_default();
	    screen.monitors_changed.connect(this.on_monitors_changed);
	    screen.size_changed.connect(this.on_size_changed);
	    
	    /* Shared GMenuLoader */
	    this.gmenu_loader = new GMenuLoader();
	    
	    /* Styling */
	    Gtk.CssProvider css_provider = new Gtk.CssProvider();
	    css_provider.load_from_data(@"
		.initialization { background-color: #000; }
		#tutorial { background: transparent; }
		.tutorial-page { background-color: @vera-color; }",
		-1
	    );
	    
	    Gtk.StyleContext.add_provider_for_screen(
		Gdk.Screen.get_default(),
		css_provider,
		Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	    );
	}

	public void startup(StartupPhase phase) {
	    /**
	     * Startups the plugin.
	    */

	    if (phase == StartupPhase.DESKTOP || phase == StartupPhase.SESSION) {
		
		this.populate_screens();

	    }

	}

	public void shutdown() {
	    /**
	     * Shutdown.
	    */
	    
	    foreach (Gtk.Window window in this.window_list) {
		window.destroy();
	    }
	    
	}

    }
}

[ModuleInit]
public void peas_register_types(GLib.TypeModule module)
{
    Peas.ObjectModule objmodule = module as Peas.ObjectModule;
    objmodule.register_extension_type(typeof(VeraPlugin), typeof(DesktopPlugin.Plugin));
}

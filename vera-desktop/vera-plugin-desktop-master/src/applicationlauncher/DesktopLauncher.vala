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

    public class DesktopLauncher : Gtk.Revealer {

	/**
	 * The DesktopLauncher widget.
	*/
	
	public bool searching { get; private set; default=false; }
	
	public string current_keyword { get; private set; }
	
	public const int ITEM_WIDTH = 50;
	public const int ITEM_HEIGHT = 50;
	
	private int max_item_number;
	
	private int current_item = 0;
	private int current_search_length = 0;
	
	public int current_page { get; private set; default=1; }
	public int last_page { get; private set; default=1; }
	
	public signal void launcher_closed();
	public signal void launcher_opened();
	
	private Gtk.IconTheme icon_theme = Gtk.IconTheme.get_default();

        private DesktopWindow parent_window;
        private Settings settings;
	private ApplicationLauncher application_launcher;
	
	private Gtk.Box container;

	private Gtk.SearchBar bar;
	private Gtk.SearchEntry search;
	
	private Gtk.Revealer results_revealer;
	private Gtk.Box results_container;
	private Gtk.Label no_results_found;
	private Gtk.Label internet_search;
	
	private Gtk.IconView results_view;
	private Gtk.ListStore results_list;
	private Gtk.TreeModelFilter results_filter;
	
	private PageHandler page_handler;
	
	private string start_text = null;
	
	private Gtk.TreeIter? last_iter = null;
		
	private void on_search_changed() {
	    /**
	     * Fired when the search text has been changed.
	    */
	    
	    //this.show();
	    
	    if (this.search.text_length == 0) {
		
		this.results_list.clear();
		
		this.bar.search_mode_enabled = false;
		this.results_revealer.reveal_child = false;
		
		this.start_text = null;
		
		this.launcher_closed();
		this.set_reveal_child(false);
				
		//this.set_child_visible(false);
		
		return;
	    } else {
		
		//this.set_child_visible(true);
		
		if (!this.results_revealer.reveal_child)
		    this.results_revealer.reveal_child = true;
	    }
	    
	    this.current_keyword = this.search.get_text().down();
	    
	    /* Reset counters */
	    this.current_item = 0;
	    this.current_page = 1;
	    this.last_page = 1;
	    
	    if (this.start_text != null && this.current_keyword.has_prefix(this.start_text)) {
		/* Start text still valid, thus we need only to filter */
		this.results_filter.refilter();
	    } else {
		/* Start text not valid anymore, search again */
		this.results_list.clear();
		this.start_text = this.current_keyword;
	        this.application_launcher.search(this.current_keyword);
	    }

	    this.no_results_found.hide();
	    
	    this.internet_search.set_markup("Search in <i>Google</i>...");
	    
	}
	
	private bool determine_item_visibility(Gtk.TreeModel model, Gtk.TreeIter iter) {
	    /**
	     * Returns True if the item linked at iter should be visible given
	     * the current keyword, False if not.
	    */
	    
	    if (!this.searching) {	
		/*
		 * Workaround subsequent duplicate entries.
		 * 
		 * For no apparent reason, *some* iters are processed twice,
		 * thus increasing the current_item counter and fooling
		 * the page handling.
		 * To avoid this, we store the last iter and check it with
		 * the current one. If the iter is the same, simply decrease
		 * by one the current_item counter.
		 * Unfortunately we can't simply "return false" here as tests
		 * have shown that the item that actually get visualized in the
		 * IconView is the second one.
		*/		
		if (iter == this.last_iter) {
		    this.current_item--;
		} else {
		    this.last_iter = iter;
		}
		
		/*
		 * FIXME: This check is redundant on a page change.
		 * There is no reliable method currently to find if we are
		 * reprocessing because of a page switch, so for now just
		 * re do the check.
		*/
		Value infos;
		model.get_value(iter, 3, out infos);
		
		if (!(
		    ApplicationLauncher.item_matches_keyword(
			this.current_keyword,
			(DesktopAppInfo)infos
		    )
		)) {
		    return false;
		}
	    }
	    
	    /* We need to update the count */
	    this.current_item++;

	    if (this.current_item > this.max_item_number*this.last_page) {
		/* Increase last_page count */
		this.last_page++;
	    }

	    if (this.current_item > this.max_item_number*this.current_page || this.current_item <= this.max_item_number*(this.current_page-1)) {
		/* Not the right page, hiding */
		return false;
	    }
	    
	    return true;
	}
	
	private void on_search_started() {
	    /**
	     * Fired when the actual search has been started.
	    */
	    
	    if (!this.bar.search_mode_enabled)
		return;
	    
	    this.current_search_length = 0;
	    this.searching = true;
	    
	}
	
	private void on_search_finished() {
	    /**
	     * Fired when the search finished.
	    */

	    if (!this.bar.search_mode_enabled)
		return;
	    
	    this.searching = false;
	    
	}
	
	private void on_application_found(DesktopAppInfo? app) {
	    /**
	     * Fired when the ApplicationLauncher has found a suitable
	     * application.
	    */
	    
	    if (!this.bar.search_mode_enabled || app == null)
		return;

	    this.current_search_length++;

	    Gtk.TreeIter iter;
	    Gdk.Pixbuf pixbuf = icon_theme.lookup_by_gicon(app.get_icon(),48,Gtk.IconLookupFlags.FORCE_SIZE).load_icon();
	    this.results_list.insert_with_values(
		out iter,
		-1,
		0,
		app.get_name(),
		1,
		pixbuf,
		2,
		app.get_description(),
		3,
		app
	    );
	    

	}
	
	private void on_launcher_page_changed(bool next) {
	    /**
	     * Fired when the page has been changed.
	    */
	    	    	    	    
	    this.current_page = next ? this.current_page+1 : this.current_page-1;
	    this.current_item = 0;
	    this.results_filter.refilter();
	    
	}
	
	private void on_item_activated(Gtk.TreePath path) {
	    /**
	     * Fired when an item has been activated.
	    */
	    
	    Gtk.TreeIter iter;
	    this.results_filter.get_iter(out iter, path);
	    
	    Value infos;
	    this.results_filter.get_value(iter, 3, out infos);
	    	    
	    new Launcher(
		((DesktopAppInfo)infos).get_commandline().replace(
		    "%u","").replace("%U","").replace("%f","").replace(
		    "%F","").strip().split(" ")
	    ).launch();
	    
	    /* Close everything */
	    this.search.set_text("");
	    
	}
	
	public bool open_launcher(Gtk.Widget widget, Gdk.EventKey event) {
	    /**
	     * Fired when we should open the launcher (triggered by a keypress)
	    */
	    
	    this.launcher_opened();

	    this.set_reveal_child(true);
	    this.bar.handle_event(event);
	    
	    return true;
	}
	
	public void set_max_item_number() {
	    /**
	     * Calculates the max item number, and sets it.
	    */
	    
	    int max_columns, max_rows;
	    max_columns = (int)Math.floor(this.parent_window.screen_size.width / ITEM_WIDTH);
	    max_rows = (int)Math.floor((this.parent_window.screen_size.height*70)/100 / ITEM_HEIGHT);
	    this.max_item_number = max_columns+max_rows;
	    
	}
	
	public void on_parent_size_changed() {
	    /**
	     * Fired when the parent window size changed.
	    */
	    
	    /* Reset max item number */
	    this.set_max_item_number();
	    
	}
	
	public DesktopLauncher(DesktopWindow parent_window, Settings settings, GMenuLoader loader) {
	    /**
	     * Constructs the DesktopLauncher.
	    */

	    Object();
	    
	    this.name = "VeraDesktopLauncher";

	    this.bar = new Gtk.SearchBar();
	    this.add(this.bar);

            this.parent_window = parent_window;
            this.settings = settings;
	    this.application_launcher = new ApplicationLauncher(loader);
	    	    
	    /* Calculate max_item_number */
	    this.set_max_item_number();
	    
	    message("max item number %d", this.max_item_number);
	    
	    /* Build the container */
	    this.container = new Gtk.Box(Gtk.Orientation.VERTICAL, 0);
	    this.bar.add(this.container);
	    
	    /* Build the search entry */
	    this.search = new Gtk.SearchEntry();
	    this.container.pack_start(this.search, false, false, 0);
	    this.bar.connect_entry(this.search);

	    /* Size */
	    this.search.set_size_request(600, -1);
	    
	    //this.pack_start(this.searchbar, false, false, 0);
	    
	    this.search.show();
	    this.show();
	    this.set_reveal_child(false);
	    
	    /* Results */
	    this.results_revealer = new Gtk.Revealer();
	    this.results_container = new Gtk.Box(Gtk.Orientation.VERTICAL, 0);
	    this.results_revealer.add(this.results_container);
	    this.container.pack_start(this.results_revealer, false, false, 0);
	    
	    this.results_list = new Gtk.ListStore(
		4,
		typeof(string),
		typeof(Gdk.Pixbuf),
		typeof(string),
		typeof(DesktopAppInfo)
	    );
	    this.results_filter = new Gtk.TreeModelFilter(this.results_list, null);
	    this.results_filter.set_visible_func(this.determine_item_visibility);

	    this.results_view = new Gtk.IconView.with_model(this.results_filter);
	    this.results_view.set_activate_on_single_click(true);
	    this.results_view.set_text_column(0);
	    this.results_view.set_pixbuf_column(1);
	    this.results_view.set_tooltip_column(2);
	    this.results_view.set_item_width(55);
	    this.results_view.set_item_padding(2);
	    this.results_container.pack_start(this.results_view);

	    /* Pages */    
	    this.page_handler = new PageHandler();
	    this.page_handler.page_changed.connect(this.on_launcher_page_changed);
	    this.results_container.pack_start(this.page_handler, false, false, 5);
	    
	    /* Disable pages buttons */
	    this.bind_property(
		"current-page",
		this.page_handler.buttons.get(ArrowButton.Position.LEFT),
		"sensitive",
		BindingFlags.DEFAULT | BindingFlags.SYNC_CREATE,
		(binding, source, ref target) => {
		    target = !(source == 1);
		    return true;
		},
		null
	    );
	    this.bind_property(
		"current-page",
		this.page_handler.buttons.get(ArrowButton.Position.RIGHT),
		"sensitive",
		BindingFlags.DEFAULT | BindingFlags.SYNC_CREATE,
		(binding, source, ref target) => {
		    target = !(source == this.last_page);
		    return true;
		},
		null
	    );
	    /* Workaround for last-page changes done after current-page has been reset */
	    this.notify["last-page"].connect(
		() => {
		    this.page_handler.buttons.get(ArrowButton.Position.RIGHT).set_sensitive(
			!(this.current_page == this.last_page)
		    );
		}
	    );

	    /* "No results found" message */
	    this.no_results_found = new Gtk.Label("No results found.");
	    this.results_container.pack_start(this.no_results_found);
	    
	    this.internet_search = new Gtk.Label(null);
	    
	    
	    /* Events */
	    this.parent_window.size_changed.connect(this.on_parent_size_changed);
	    this.results_view.item_activated.connect(this.on_item_activated);
	    this.search.search_changed.connect(this.on_search_changed);
	    this.application_launcher.search_started.connect(this.on_search_started);
	    this.application_launcher.application_found.connect(this.on_application_found);
	    this.application_launcher.search_finished.connect(this.on_search_finished);

	}

    }

}

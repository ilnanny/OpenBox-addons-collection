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
    
    public class ArrowButton : Gtk.Button {
	
	public enum Position {
	    LEFT,
	    RIGHT
	}
	
	public ArrowButton.Position position { get; construct set; }
		
	public ArrowButton(ArrowButton.Position position) {
	    /**
	     * Creates an ArrowButton.
	    */
	    
	    Object();
	    
	    this.position = position;
	    
	    this.set_label((this.position == ArrowButton.Position.LEFT) ? "<" : ">");
	    
	}
	
    }
    
    public class PageHandler : Gtk.Box {
	
	public signal void page_changed(bool next);
	
	public HashTable<ArrowButton.Position, ArrowButton> buttons =
	    new HashTable<ArrowButton.Position, ArrowButton>(direct_hash, direct_equal);
	
	private void on_arrowbutton_clicked(Gtk.Button button) {
	    /**
	     * Fired when an arrowbutton has been clicked.
	    */
	    
	    this.page_changed((((ArrowButton)button).position == ArrowButton.Position.RIGHT));
	    
	}
	
	public PageHandler() {
	    
	    Object(orientation: Gtk.Orientation.HORIZONTAL);
	    
	    this.halign = Gtk.Align.CENTER;
	    this.valign = Gtk.Align.CENTER;
	    
	    /* Add arrow buttons */
	    ArrowButton button;
	    ArrowButton.Position position;
	    for (int i = 0; i < 2; i++) {
		position = (ArrowButton.Position)i;
		button = new ArrowButton(position);
		
		button.clicked.connect(this.on_arrowbutton_clicked);
		
		this.pack_start(button, false, false, 5);
		
		this.buttons.set(position, button);
	    }
	    
	}
	
    }
	
	
    
    public class PageButton : Gtk.RadioButton {
    
	public int page_number { get; private set; }
    
	public PageButton(Gtk.RadioButton? radio_group_member, owned int page_number) {
	    
	    Object();
	    
	    this.page_number = page_number;
	    
	    this.group = radio_group_member;
	    ((Gtk.ToggleButton)this).draw_indicator = false;
	    
	    this.set_label(page_number.to_string());
	    
	}
    }

    public class LauncherPages : Gtk.Box {
	
	/**
	 * The pages of the launcher.
	*/
		
	public signal void page_changed(int new_page);
	
	public LauncherPages() {
	    
	    Object(orientation: Gtk.Orientation.HORIZONTAL);
	    
	    /* Add first page */
	    this.update_page_number(1);
	    
	    this.halign = Gtk.Align.CENTER;
	    this.valign = Gtk.Align.CENTER;
	    
	}
	
	private void on_button_toggled(PageButton button, int page) {
	    
	    this.page_changed(page);
	    
	}
	
	public void update_page_number(int new_page) {
	    /**
	     * Creates/Removes buttons.
	    */
	    	    
	    PageButton first_page = null;
	    PageButton button;
	    int count = 0;
	    
	    /* Destroy current buttons */
	    this.foreach(
		(child) => {
		    child.destroy();
		}
	    );
	    
	    while (count < new_page) {
		count++;
		
		button = new PageButton(first_page, count);
		button.toggled.connect(
		    (_button) => {
			PageButton page_button = (PageButton)button;
			if (page_button.get_active()) {
			    this.page_changed(((PageButton)page_button).page_number);
			}
		    }
		);
		button.show();
		this.pack_start(button, false, false, 5);
		
		if (first_page == null) {
		    /* This is the first page, save it */
		    first_page = button;
		}
	    }
	    
	}
	
    }
    
}

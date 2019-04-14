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
	
	public class GMenuLoader : Object {
		/**
		 * This class loads and maintains the GMenuTree.
		*/
		
		public GMenu.Tree tree { get; private set; }
		public GMenu.TreeDirectory root { get; private set; }
		
		public bool enabled { get; construct set; default=true; }
		
		public GMenuLoader() {
			/**
			 * Constructs this class.
			*/
			
			this.tree = new GMenu.Tree(
				"%sapplications.menu".printf(
					(
						(Environment.get_variable("XDG_MENU_PREFIX") != null) ?
						Environment.get_variable("XDG_MENU_PREFIX") :
						"vera-"
					)
				),
				GMenu.TreeFlags.SORT_DISPLAY_NAME
			);
			
			/* Load */
			try {
				/* Are there any async methods? */
				this.tree.load_sync();
			} catch (Error e) {
				warning("Unable to load ApplicationLauncher: %s", e.message);
				this.enabled = false;
			}
			
			this.root = this.tree.get_root_directory();
		}
		
	}
		

	public class ApplicationLauncher : Object {
		
		/**
		 * A UI toolkit-agnostic application launcher.
		*/
		
		public bool enabled {
			get {
				return this.loader.enabled;
			}
		}
		
		private GMenuLoader loader;
		
		public signal void search_started();
		public signal void application_found(DesktopAppInfo? app);
		public signal void search_finished();
		
		private Rand random = new Rand();
		private uint SEARCH_ID;
		
		public ApplicationLauncher(GMenuLoader loader) {
			/**
			 * Constructs this class.
			*/
			
			this.loader = loader;
		}
		
		public static bool item_matches_keyword(string keyword, DesktopAppInfo? infos) {
			/**
			 * Returns true if the informations in the given DesktopAppInfo matches
			 * the given keyword, false if not.
			*/
			
			string name, description;
			
			if (infos == null) {
				return false;
			}
			
			name = infos.get_name();
			description = infos.get_description();
			
			if ((name != null && keyword.down() in name.down()) || (description != null && keyword.down() in description.down())) {
				/* Yay */
				
				return true;
			} else {
				return false;
			}
		}
		
		public void search(string keyword, GMenu.TreeDirectory? directory = null, uint? _internal_id = null) {
			/**
			 * Makes an application search using the specified keyword.
			 * 
			 * This method invokes application_found() whenever it finds an
			 * application matching the keyword, so to actually make something
			 * useful you must subscribe to that signal too.
			*/
			
			
			uint internal_id;
			if (_internal_id == null) {
				internal_id = this.random.next_int();
				this.SEARCH_ID = internal_id;
			} else {
				internal_id = _internal_id;
			}
			
			if (directory == null)
				this.search_started();
			
			GMenu.TreeIter iter = ((directory != null) ? directory : this.loader.root).iter();
			GMenu.TreeItemType type;
			string name, description;
			while ((type = iter.next()) != GMenu.TreeItemType.INVALID) {
				
				/* Still valid? */
				if (this.SEARCH_ID != internal_id)
					/* No. */
					return;
				
				if (type == GMenu.TreeItemType.DIRECTORY) {
					/* Directory, re run this method on it */
					
					this.search(keyword, iter.get_directory(), internal_id);
					
				} else if (type == GMenu.TreeItemType.ENTRY) {
					/* Entry */
					
					DesktopAppInfo infos = iter.get_entry().get_app_info();
					
					if (infos != null && item_matches_keyword(keyword, infos))  {
						/* Yay */
						
						this.application_found(infos);
						
					}
					
				}
			}
			
			if (directory == null) {
				this.search_finished();
			}
			
		}
		
	}

}

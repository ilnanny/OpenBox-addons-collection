# -*- coding: utf-8 -*-
#
# desktop - vera-plugin-desktop module for Vera Control Center
# Copyright (C) 2014  Semplice Project
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Authors:
#    Eugenio "g7" Paolantonio <me@medesimo.eu>
#

import os
import quickstart
import configparser

from gi.repository import GdkPixbuf, GObject, Gio, Gtk, Gdk

from veracc.utils import Settings

SUPPORTED_MIMETYPES = (
	"image/bmp",
	"image/gif",
	"image/jpeg",
	"image/x-portable-bitmap",
	"image/png",
	"image/xbm",
)

class Properties(GObject.GObject):
	"""
	This class contains some client-side properties that we'll syncronize
	with dconf using bind(_with_convert).
	"""
	
	properties = (
		"current-wallpapers",
		"current-selected-monitor"
	)
	
	__gproperties__ = {
		"current-wallpapers" : (
			GObject.TYPE_STRV,
			"Current wallpapers",
			"The currently set wallpapers",
			GObject.PARAM_READWRITE
		),
		"current-selected-monitor" : (
			GObject.TYPE_INT,
			"Currently selected monitor",
			"The currently selected monitor",
			0,  # min
			100, # max
			0,  # default
			GObject.PARAM_READWRITE
		),
	}
	
	def __init__(self):
		
		super().__init__()
		
		self.current_wallpapers = []
		self.current_selected_monitor = 0

	def do_get_property(self, property):
		"""
		Returns the value of the specified property
		"""
		
		if property.name in self.properties:
			return getattr(self, property.name.replace("-","_"))
		else:
			raise AttributeError("unknown property %s" % property.name)
	
	def do_set_property(self, property, value):
		"""
		You can't set properties.
		"""
		
		if property.name in self.properties:
			setattr(self, property.name.replace("-","_"), value)
		else:
			raise AttributeError("unknown property %s" % property.name)
	

@quickstart.builder.from_file("./modules/desktop/desktop.glade")
class Scene(quickstart.scenes.BaseScene):
	""" Desktop preferences. """
	
	events = {
		"item-activated": ("wallpapers",),
		"response": ("add_background_window", "about_background_dialog"),
		"update_preview" : ("add_background_window",),
		"toggled": ("select_entire_directories",),
		"clicked": (
			"add_background",
			"remove_background",
			"about_button"
		),
	}

	wallpapers = {}
	
	infos = configparser.ConfigParser()
	
	properties = Properties()
		
	def new_rgba_from_string(self, string):
		"""
		Given a string, return a parsed Gdk.RGBA.
		"""

		rgba = Gdk.RGBA()
		rgba.parse(string)
		
		return rgba

	def get_selection(self):
		"""
		Returns the TreeIter of the current selection.
		"""
		
		item = self.objects.wallpapers.get_selected_items()[0]
		
		return self.objects.wallpaper_list.get_iter(item)

	def set_selection(self, path):
		"""
		Sets the selected wallpaper given its path (not TreePath, the path
		of the wallpaper).
		"""
		
		if path in self.wallpapers:
			self.objects.wallpapers.select_path(self.objects.wallpaper_list.get_path(self.wallpapers[path]))

			# Show/Hide the About button
			if os.path.basename(self.objects.wallpaper_list.get_value(self.get_selection(), 0)) in self.infos:
				GObject.idle_add(self.objects.about_button.show)
			else:
				GObject.idle_add(self.objects.about_button.hide)
		else:
			# The wallpaper is not in our list, so we need to add it now...
			if os.path.exists(path):
				self.add_wallpaper_to_list(path)
				return self.set_selection(path) # Restart
	
	def on_select_entire_directories_toggled(self, checkbutton):
		"""
		Fired when the user presses the "Select entire directories"
		CheckButton in the FileChooser.
		"""
		
		self.objects.add_background_window.set_action(
			Gtk.FileChooserAction.OPEN if not checkbutton.get_active() else Gtk.FileChooserAction.SELECT_FOLDER
		)
	
	def on_add_background_window_update_preview(self, window):
		"""
		Fired when the preview of the window should be updated.
		"""
		
		filename = window.get_preview_filename()
		if not os.path.isfile(filename):
			window.set_preview_widget_active(False)
			return
		else:
			window.set_preview_widget_active(True)
		
		try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
				window.get_preview_filename(),
				150,
				200,
				True
			)
			self.objects.preview.set_from_pixbuf(pixbuf)
		except:
			window.set_preview_widget_active(False)
	
	def on_add_background_window_response(self, window, response_id):
		"""
		Fired when the user presses an action button in the FileChooser
		shown when adding a new wallpaper/directory.
		"""
		
		if response_id == Gtk.ResponseType.ACCEPT:
			# Add background
			_queue_repopulation = False
			for wall in window.get_filenames():
				if window.get_action() == Gtk.FileChooserAction.OPEN:
					# Single files, no directories, so append to "include"
					
					if wall in self.wallpapers:
						# Already there!
						continue
					
					include = self.settings.get_strv("background-include")
					exclude = self.settings.get_strv("background-exclude")
					
					if wall in exclude:
						# Already excluded, so we can simply remove it
						# from the list
						exclude.remove(wall)
					elif wall not in include:
						# Not excluded, append to the include list
						include.append(wall)
					
					self.add_wallpaper_to_list(wall)

					self.settings.set_strv("background-include", include)
					self.settings.set_strv("background-exclude", exclude)
				else:
					# Entire directories, append them to the search path
					
					background_search_paths = self.settings.get_strv("background-search-paths")
					
					if wall in background_search_paths:
						# Already there!
						continue
					
					background_search_paths.append(wall)
					
					self.settings.set_strv("background-search-paths", background_search_paths)
					
					# Queue
					_queue_repopulation = True
			
			if _queue_repopulation:
				# Repopulate
				self.populate_wallpapers()
		
		window.hide()
	
	def on_about_background_dialog_response(self, window, response_id):
		"""
		Fired when the user closes the about background dialog.
		"""
		
		window.hide()
	
	def on_about_button_clicked(self, button):
		"""
		Fired when the about button has been clicked.
		"""
		
		# Populate
		itr = self.get_selection()
		wall = os.path.basename(self.objects.wallpaper_list.get_value(itr, 0))
		
		self.objects.name.set_label(
			self.infos[wall]["Name"] if "Name" in self.infos[wall] else ""
		)
		self.objects.description.set_label(
			self.infos[wall]["Description"] if "Description" in self.infos[wall] else ""
		)
		self.objects.author.set_label(
			self.infos[wall]["Author"] if "Author" in self.infos[wall] else ""
		)
		self.objects.license.set_label(
			self.infos[wall]["License"] if "License" in self.infos[wall] else ""
		)
		
		if "LicenseLink" in self.infos[wall]:
			self.objects.license.set_sensitive(True)
			self.objects.license.set_uri(self.infos[wall]["LicenseLink"])
		else:
			self.objects.license.set_sensitive(False)
			self.objects.license.set_uri("")
		
		if "Link" in self.infos[wall]:
			self.objects.name.set_sensitive(True)
			self.objects.name.set_uri(self.infos[wall]["Link"])
		else:
			self.objects.name.set_sensitive(False)
			self.objects.name.set_uri("")
		
		self.objects.about_background_dialog.run()
	
	def on_add_background_clicked(self, button):
		"""
		Fired when the add background button has been clicked.
		"""
		
		self.objects.add_background_window.run()

	def on_remove_background_clicked(self, button):
		"""
		Fired when the remove background button has been clicked.
		"""
		
		itr = self.get_selection()
		wall = self.objects.wallpaper_list.get_value(itr, 0)
		
		# If wallpaper is in background-include, remove from there.
		# Otherwise, add an exclusion rule
		include = self.settings.get_strv("background-include")
		if wall in include:
			include.remove(wall)
			self.settings.set_strv("background-include", include)
		else:
			exclude = self.settings.get_strv("background-exclude")
			exclude.append(wall)
			self.settings.set_strv("background-exclude", exclude)
		
		new = self.objects.wallpaper_list.iter_next(itr)
		if not new:
			# Unable to set next (probably this was the last iter), so
			# use the previous
			new =  self.objects.wallpaper_list.iter_previous(itr)
			
			# If new == None (again), probably this was the only one wallpaper.
			# We can't do anything, so we'll leave an inconsistent state
		
		if new:
			path = self.objects.wallpaper_list.get_path(new)
			self.objects.wallpapers.select_path(path)
			self.objects.wallpapers.emit("item_activated", path)
		
		self.objects.wallpaper_list.remove(itr)
		del self.wallpapers[wall]
	
	def on_wallpapers_item_activated(self, widget, path):
		"""
		Fired when the user changes the wallpaper.
		"""
				
		itr = self.objects.wallpaper_list.get_iter(path)
		wall = self.objects.wallpaper_list.get_value(itr, 0)
		# Show/Hide the About button
		if os.path.basename(wall) in self.infos:
			GObject.idle_add(self.objects.about_button.show)
		else:
			GObject.idle_add(self.objects.about_button.hide)
		
		current_wallpapers = self.properties.current_wallpapers
		if self.properties.current_selected_monitor == 0:
			# "All monitors", change only the first item in the array
			current_wallpapers[0] = wall
		else:
			# Single monitor, change the relevant item
			current_wallpapers[self.properties.current_selected_monitor-1] = wall
		
		self.properties.set_property("current-wallpapers", current_wallpapers)

	def add_wallpaper_to_list(self, path, set=False):
		"""
		Appends the given wallpaper to the list.
		"""
		
		if Gio.File.new_for_path(path).query_info(
			Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
			Gio.FileQueryInfoFlags.NONE
		).get_content_type() in SUPPORTED_MIMETYPES:
			try:
				itr = self.objects.wallpaper_list.append(
					(
						path,
						GdkPixbuf.Pixbuf.new_from_file_at_scale(
							path,
							150,
							200,
							True
						)
					)
				)
				
				self.wallpapers[path] = itr
				
				if set:
					self.set_selection(path)
			except:
				pass
	
	def load_wallpaperpack(self, path):
		"""
		Loads the given wallpaperpack.
		"""
		
		try:
			self.infos.read(path)
		except:
			# FIXME: Implement true logging
			print("Unable to load wallpaperpack %s" % path)
	
	@quickstart.threads.thread
	def populate_wallpapers(self):
		"""
		Populates the wallpaper_list.
		"""
		
		# Clear things up
		self.wallpapers = {}
		self.objects.wallpaper_list.clear()
		
		excluded = self.settings.get_strv("background-exclude")
		include = self.settings.get_strv("background-include")
		
		default = self.settings.get_strv("image-path")[0]
		
		for directory in self.settings.get_strv("background-search-paths"):
			for root, dirs, files in os.walk(directory):
				for wall in files:
					path = os.path.join(root, wall)
					if not os.path.exists(path) or path in excluded: continue
					
					# .wallpaperpack file?
					if wall.endswith(".wallpaperpack"):
						# Load it
						self.load_wallpaperpack(path)
					
					GObject.idle_add(self.add_wallpaper_to_list, path, (path == default))
		
		# Add to the Included wallpapers
		for wallpaper in include:
			if not os.path.exists(wallpaper):
				continue

			GObject.idle_add(self.add_wallpaper_to_list, wallpaper, (path == default))
		
		#GObject.idle_add(self.set_selection, self.settings.get_strv("image-path")[0])
		GObject.idle_add(self.objects.wallpapers.set_sensitive, True)
	
	def on_current_selected_monitor_changed(self, properties, param):
		"""
		Fired when the current-selected-monitor property in Properties has been changed.
		"""
		
		if self.properties.current_selected_monitor == 0:
			# All monitors, use the first wallpaper everywhere
			self.properties.set_property(
				"current-wallpapers",
				[(self.properties.current_wallpapers[x] if x == 0 else "") for x in range(0, self.monitor_number)]
			)
			self.set_selection(self.properties.current_wallpapers[0])
		else:
			# Single monitor, simply re-set selection
			self.set_selection(
				self.properties.current_wallpapers[self.properties.current_selected_monitor-1] if self.properties.current_wallpapers[
					self.properties.current_selected_monitor-1] != "" else self.properties.current_wallpapers[0]
			)
			
	def prepare_scene(self):
		""" Called when doing the scene setup. """
		
		self.scene_container = self.objects.main
		
		self.objects.wallpapers.set_pixbuf_column(1)
		
		self.settings = Settings("org.semplicelinux.vera.desktop")
		self.openbox_settings = Settings("org.semplicelinux.vera.openbox")
		
		# Build monitor list
		self.monitor_number = Gdk.Screen.get_default().get_n_monitors()
		
		# Build monitor chooser
		self.monitor_model = Gtk.ListStore(str)
		self.objects.monitor_chooser.set_model(self.monitor_model)
		renderer = Gtk.CellRendererText()
		self.objects.monitor_chooser.pack_start(renderer, True)
		self.objects.monitor_chooser.add_attribute(renderer, "text", 0)

		# Current wallpaper		
		self.settings.bind_with_convert(
			"image-path",
			self.properties,
			"current-wallpapers",
			lambda x: [(x[y] if y < len(x) else "") for y in range(0, self.monitor_number)],
			lambda x: x
		)

		# Populate monitor model
		self.monitor_model.insert_with_valuesv(-1, [0], [_("All monitors")]) # "All monitors"
		for monitor in range(1, self.monitor_number+1):
			self.monitor_model.insert_with_valuesv(-1, [0], [_("Monitor %d") % (monitor)])
		self.objects.monitor_chooser.set_active(0)
		self.objects.monitor_chooser.bind_property(
			"active",
			self.properties,
			"current-selected-monitor",
			GObject.BindingFlags.SYNC_CREATE
		)
		self.properties.connect("notify::current-selected-monitor", self.on_current_selected_monitor_changed)
		
		if self.properties.current_wallpapers.count("") == self.monitor_number-1:
			# Probably we are in an "All monitors" situation
			# We do not use set_active() to avoid trigger an useless write action
			# to dconf.
			self.set_selection(self.properties.current_wallpapers[0])
		else:
			# Single monitor, default to Monitor 1
			self.objects.monitor_chooser.set_active(1)
		
		# Show it if we should
		if self.monitor_number > 1: self.objects.monitor_chooser.show()
		
		# Background color
		self.settings.bind_with_convert(
			"background-color",
			self.objects.background_color,
			"rgba",
			lambda x: self.new_rgba_from_string(x),
			lambda x: x.to_string()
		)
		
		# Background mode
		renderer = Gtk.CellRendererText()
		self.objects.background_mode.pack_start(renderer, True)
		self.objects.background_mode.add_attribute(renderer, "text", 1)
		self.settings.bind(
			"background-mode",
			self.objects.background_mode,
			"active_id"
		)
		
		# Background random enabled?
		self.settings.bind(
			"background-random-enabled",
			self.objects.background_random_enabled,
			"active"
		)
		
		# Background random timeout
		self.settings.bind(
			"background-random-timeout",
			self.objects.background_random_timeout,
			"value"
		)
		
		# Ensure the random timeout spinbutton is insensitive if
		# the checkbutton is not active
		self.objects.background_random_enabled.bind_property(
			"active",
			self.objects.background_random_timeout_spin,
			"sensitive",
			GObject.BindingFlags.SYNC_CREATE
		)
		
		# Virtual desktops
		self.openbox_settings.bind(
			"desktops-number",
			self.objects.virtual_desktops_spin,
			"value"
		)
		
		# Prepare the "Add background" dialog...
		self.objects.add_background_window.add_buttons(
			_("_Cancel"),
			Gtk.ResponseType.CANCEL,
			_("_Open"),
			Gtk.ResponseType.ACCEPT
		)
		self.objects.all_files.set_name(_("All Files"))
		self.objects.image_filter.set_name(_("Images"))
		self.objects.add_background_window.add_filter(self.objects.image_filter)
		self.objects.add_background_window.add_filter(self.objects.all_files)
		
		# Prepare the "About background" dialog...
		self.objects.about_background_dialog.add_buttons(
			_("_Close"),
			Gtk.ResponseType.CLOSE
		)
		
		self.objects.main.show_all()
				
		# Ensure the user doesn't change wallpaper while we are builing the list
		GObject.idle_add(self.objects.wallpapers.set_sensitive, False)
		
		self.populate_wallpapers()

# -*- coding: utf-8 -*-
#
# theme - Appearance module for Vera Control Center
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

from veracc.widgets.CommonFrame import CommonFrame

from veracc.utils import Settings

from gi.repository import Gtk, Gdk, GObject
import quickstart

class GtkThemeFrame(CommonFrame):
	"""
	This is the Frame with controls to change the GTK+ theme.
	"""

	SEARCH_PATH = ("/usr/share/themes", os.path.expanduser("~/.themes"))

	@property
	def available_themes(self):
		""" Returns the available themes, searching in SEARCH_PATH. """
		
		themes = []
		
		for directory in self.SEARCH_PATH:
			if not os.path.exists(directory):
				continue
			
			for theme in os.listdir(directory):
				
				path = os.path.join(directory, theme)
				
				if theme not in themes and (
					os.path.isdir(path) and os.path.exists(os.path.join(path, "gtk-3.0"))
				):
					themes.append(theme)
		
		themes.sort()
		return themes

	@quickstart.threads.on_idle
	def populate_themes(self):
		""" Populates the theme list. """
		
		self.themes = {}
		
		count = -1
		for theme in self.available_themes:
			count += 1
			
			self.combobox.append_text(theme)
			
			# Add to self.themes
			self.themes[theme] = count
		
		# Bind
		self.settings.bind_with_convert(
			"theme-name",
			self.combobox,
			"active",
			lambda x: self.themes[x] if x in self.themes else -1,
			lambda x: self.combobox.get_active_text()
		)
	
	def new_rgba_from_string(self, string):
		"""
		Given a string, return a parsed Gdk.RGBA.
		"""
		
		rgba = Gdk.RGBA()
		rgba.parse(string)
		
		return rgba
	
	def __init__(self, settings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Widgets"))
		
		# Settings
		self.settings = settings
		self.desktopsettings = Settings("org.semplicelinux.vera.desktop")
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Combobox
		self.combobox_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.combobox = Gtk.ComboBoxText()
		self.combobox_label = Gtk.Label(_("Theme"))
		self.combobox_label.set_alignment(0, 0.50)
		
		self.combobox_container.pack_start(self.combobox_label, True, True, 0)
		self.combobox_container.pack_start(self.combobox, False, False, 0)
		
		# Populate it and bind
		self.populate_themes()
		
		# Images in buttons
		self.button_images = Gtk.CheckButton(_("Show images in buttons"))
		self.settings.bind(
			"button-images",
			self.button_images,
			"active"
		)
		
		# Images in menus
		self.menu_images = Gtk.CheckButton(_("Show images in menus"))
		self.settings.bind(
			"menu-images",
			self.menu_images,
			"active"
		)
		
		# Vera color
		self.vera_color_enabled = Gtk.CheckButton(_("Use custom color for selected items (when supported)"))
		self.desktopsettings.bind(
			"vera-color-enabled",
			self.vera_color_enabled,
			"active"
		)
		
		# Vera color selection
		self.vera_color_selection = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.vera_color_selection.set_margin_start(20)
		self.vera_color_enabled.bind_property(
			"active",
			self.vera_color_selection,
			"sensitive",
			GObject.BindingFlags.SYNC_CREATE
		)
		self.vera_color_from_wallpaper = Gtk.RadioButton.new_with_label_from_widget(None, _("Pick color from the current wallpaper"))
		self.vera_color_manual_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.vera_color_manual_color = Gtk.ColorButton()
		self.desktopsettings.bind_with_convert(
			"vera-color",
			self.vera_color_manual_color,
			"rgba",
			lambda x: self.new_rgba_from_string(x),
			lambda x: x.to_string()
		)
		self.vera_color_manual_color.set_sensitive(True)
		self.vera_color_manual = Gtk.RadioButton.new_with_label_from_widget(self.vera_color_from_wallpaper, _("Use this color"))
		self.vera_color_manual.bind_property(
			"active",
			self.vera_color_manual_color,
			"sensitive",
			GObject.BindingFlags.SYNC_CREATE
		)
		self.desktopsettings.bind(
			"vera-color-lock",
			self.vera_color_manual,
			"active"
		)
		self.vera_color_manual_container.pack_start(self.vera_color_manual, True, True, 0)
		self.vera_color_manual_container.pack_start(self.vera_color_manual_color, False, False, 0)
		
		self.vera_color_selection.pack_start(self.vera_color_from_wallpaper, False, False, 0)
		self.vera_color_selection.pack_start(self.vera_color_manual_container, False, False, 2)
		
		self.main_container.pack_start(self.combobox_container, False, False, 0)
		self.main_container.pack_start(self.button_images, False, False, 2)
		self.main_container.pack_start(self.menu_images, False, False, 2)
		self.main_container.pack_start(self.vera_color_enabled, False, False, 2)
		self.main_container.pack_start(self.vera_color_selection, False, False, 2)
		
		self.get_alignment().add(self.main_container)

class OpenboxThemeFrame(CommonFrame):
	"""
	This is the Frame with controls to change the Openbox theme.
	"""

	SEARCH_PATH = ("/usr/share/themes", os.path.expanduser("~/.themes"))

	@property
	def available_themes(self):
		""" Returns the available themes, searching in SEARCH_PATH. """
		
		themes = []
		
		for directory in self.SEARCH_PATH:
			if not os.path.exists(directory):
				continue
			
			for theme in os.listdir(directory):
				
				path = os.path.join(directory, theme)
				
				if theme not in themes and (
					os.path.isdir(path) and os.path.exists(os.path.join(path, "openbox-3"))
				):
					themes.append(theme)
		
		themes.sort()
		return themes

	@quickstart.threads.on_idle
	def populate_themes(self):
		""" Populates the theme list. """
		
		self.themes = {}
		
		count = -1
		for theme in self.available_themes:
			count += 1
			
			self.combobox.append_text(theme)
			
			# Add to self.themes
			self.themes[theme] = count
		
		# Bind
		self.openboxsettings.bind_with_convert(
			"theme-name",
			self.combobox,
			"active",
			lambda x: self.themes[x] if x in self.themes else -1,
			lambda x: self.combobox.get_active_text()
		)
	
	def on_gtk_theme_changed(self, settings, key):
		"""
		Fired when the gtk theme has been changed.
		"""
		
		theme = settings.get_string(key)
		
		if theme in self.available_themes:
			self.openboxsettings.set_string("theme-name", theme)

	def __init__(self, settings, openboxsettings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Windows"))
		
		# Settings
		self.settings = settings
		self.openboxsettings = openboxsettings
		
		# Change openbox theme when the main theme changes
		self.settings.connect("changed::theme-name", self.on_gtk_theme_changed)
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Combobox
		self.combobox_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.combobox = Gtk.ComboBoxText()
		self.combobox_label = Gtk.Label(_("Theme"))
		self.combobox_label.set_alignment(0, 0.50)
		
		self.combobox_container.pack_start(self.combobox_label, True, True, 0)
		self.combobox_container.pack_start(self.combobox, False, False, 0)

		# Window icon
		self.window_icon = Gtk.CheckButton(_("Show the window icon"))
		self.openboxsettings.bind_with_convert(
			"title-layout",
			self.window_icon,
			"active",
			lambda x: True if "N" in x else False,
			lambda x: self.openboxsettings.get_string("title-layout").replace("N","") if not x else "N%s" % self.openboxsettings.get_string("title-layout")
		)

		# Populate it and bind
		self.populate_themes()

		self.main_container.pack_start(self.combobox_container, False, False, 0)
		self.main_container.pack_start(self.window_icon, False, False, 2)

		self.get_alignment().add(self.main_container)

class IconThemeFrame(CommonFrame):
	"""
	This is the Frame with controls to change the Icon Theme.
	"""

	SEARCH_PATH = ("/usr/share/icons", os.path.expanduser("~/.icons"))

	@property
	def available_themes(self):
		""" Returns the available themes, searching in SEARCH_PATH. """
		
		themes = []
		
		for directory in self.SEARCH_PATH:
			if not os.path.exists(directory):
				continue
			
			for theme in os.listdir(directory):
				
				path = os.path.join(directory, theme)
				
				if theme not in themes and (
					os.path.isdir(path)
					and os.path.exists(os.path.join(path, "index.theme"))
					and not os.path.exists(os.path.join(path, "cursor.theme"))
				):
					themes.append(theme)
		
		themes.sort()
		return themes

	@quickstart.threads.on_idle
	def populate_themes(self):
		""" Populates the theme list. """
		
		self.themes = {}
		
		count = -1
		for theme in self.available_themes:
			count += 1
			
			self.combobox.append_text(theme)
			
			# Add to self.themes
			self.themes[theme] = count
		
		# Bind
		self.settings.bind_with_convert(
			"icon-theme-name",
			self.combobox,
			"active",
			lambda x: self.themes[x] if x in self.themes else -1,
			lambda x: self.combobox.get_active_text()
		)
		
	
	def __init__(self, settings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Icons"))
		
		# Settings
		self.settings = settings
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Combobox
		self.combobox_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.combobox = Gtk.ComboBoxText()
		self.combobox_label = Gtk.Label(_("Icon theme"))
		self.combobox_label.set_alignment(0, 0.50)
		
		self.combobox_container.pack_start(self.combobox_label, True, True, 0)
		self.combobox_container.pack_start(self.combobox, False, False, 0)
		
		# Preview
		self.preview_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.preview_container.set_halign(Gtk.Align.CENTER)
		for icon in ("folder", "desktop", "image", "application-x-executable"):
			self.preview_container.pack_start(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG), False, False, 5)
		
		# Populate it and bind
		self.populate_themes()
				
		self.main_container.pack_start(self.combobox_container, False, False, 0)
		self.main_container.pack_start(self.preview_container, False, False, 15)
		
		self.get_alignment().add(self.main_container)

class CursorThemeFrame(CommonFrame):
	"""
	This is the Frame with controls to change the Cursor Theme.
	"""

	SEARCH_PATH = ("/usr/share/icons", os.path.expanduser("~/.icons"))
	
	@property
	def available_themes(self):
		""" Returns the available themes, searching in SEARCH_PATH. """
		
		themes = []
		
		for directory in self.SEARCH_PATH:
			if not os.path.exists(directory):
				continue
			
			for theme in os.listdir(directory):
				
				path = os.path.join(directory, theme)
				
				if theme not in themes and (
					os.path.isdir(path)
					and os.path.exists(os.path.join(path, "cursor.theme"))
				):
					themes.append(theme)
		
		themes.sort()
		return themes

	@quickstart.threads.on_idle
	def populate_themes(self):
		""" Populates the theme list. """
		
		self.themes = {}
		
		count = -1
		for theme in self.available_themes:
			count += 1
			
			self.combobox.append_text(theme)
			
			# Add to self.themes
			self.themes[theme] = count
		
		# Bind
		self.settings.bind_with_convert(
			"cursor-theme-name",
			self.combobox,
			"active",
			lambda x: self.themes[x] if x in self.themes else -1,
			lambda x: self.combobox.get_active_text()
		)
				
		# Connect changed in order to show the warning when needed
		self.combobox.connect("changed", self.on_combobox_changed)
	
	def on_combobox_changed(self, combobox):
		"""
		Fired when the combobox has been changed.
		"""
				
		self.warning.set_visible(
			not (self.combobox.get_active_text() == self.current_theme)
		)
	
	def __init__(self, settings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Cursor"))
		
		# Settings
		self.settings = settings
		self.current_theme = self.settings.get_string("cursor-theme-name")
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Combobox
		self.combobox_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.combobox = Gtk.ComboBoxText()
		self.combobox_label = Gtk.Label(_("Cursor theme"))
		self.combobox_label.set_alignment(0, 0.50)
		
		self.combobox_container.pack_start(self.combobox_label, True, True, 0)
		self.combobox_container.pack_start(self.combobox, False, False, 0)
		
		# Warning
		self.warning = Gtk.Label()
		self.warning.set_markup("<i>%s</i>" % _("You need to logout to apply the changes."))
		self.warning.set_no_show_all(True)
		self.warning.set_line_wrap(True)
		
		# Populate it and bind
		self.populate_themes()
		
		self.main_container.pack_start(self.combobox_container, False, False, 0)
		self.main_container.pack_start(self.warning, False, False, 15)
		
		self.get_alignment().add(self.main_container)

class GtkTheme(Gtk.Box):
	""" The 'Theme' page. """
	
	def __init__(self, settings, openboxsettings):
		"""
		Initializes the page.
		"""
		
		super().__init__(orientation=Gtk.Orientation.VERTICAL)
		
		self.pack_start(GtkThemeFrame(settings), False, False, 2)
		self.pack_start(OpenboxThemeFrame(settings, openboxsettings), False, False, 2)
		self.pack_start(IconThemeFrame(settings), False, False, 2)
		self.pack_start(CursorThemeFrame(settings), False, False, 2)
		
		self.show_all()

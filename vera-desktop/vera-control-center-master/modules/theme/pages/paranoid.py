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

class DesktopEffectsFrame(CommonFrame):
	"""
	The Desktop Effects frame.
	"""
	
	def __init__(self, gtksettings, comptonsettings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("General"))
		
		# Settings
		self.gtksettings = gtksettings
		self.comptonsettings = comptonsettings
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Animations
		self.animations = Gtk.CheckButton(_("Enable animations in applications"))
		self.gtksettings.bind(
			"enable-animations",
			self.animations,
			"active"
		)
		
		# Window effects
		self.compton_enabled = Gtk.CheckButton(_("Enable window effects"))
		if os.path.exists("/usr/bin/compton"):
			# Bind property only if we are sure compton is present
			self.comptonsettings.bind(
				"enable-visual-effects",
				self.compton_enabled,
				"active"
			)
		else:
			# Remove sensitiveness from the checkbutton
			self.compton_enabled.set_sensitive(False)
		
		self.main_container.pack_start(self.animations, True, True, 2)
		self.main_container.pack_start(self.compton_enabled, True, True, 2)

		self.get_alignment().add(self.main_container)

class ShadowFrame(CommonFrame):
	"""
	The Shadows Frame
	"""
	
	def update_shadow_color(self, settings, color):
		"""
		Fired when a shadow color has been changed in dconf.
		"""
		
		if self.updating_shadows: return
		
		rgba = self.shadow_color_button.get_rgba()
		value = settings.get_double(color)
		
		if color == "shadow-red":
			rgba.red = value
		elif color == "shadow-blue":
			rgba.blue = value
		elif color == "shadow-green":
			rgba.green = value
		
		self.shadow_color_button.set_rgba(rgba)
	
	def store_shadow_color(self, button):
		"""
		Stores in dconf the shadow color.
		"""
		
		self.updating_shadows = True
		
		rgba = button.get_rgba()
		
		self.comptonsettings.set_double("shadow-red", rgba.red)
		self.comptonsettings.set_double("shadow-blue", rgba.blue)
		self.comptonsettings.set_double("shadow-green", rgba.green)
		
		self.updating_shadows = False
	
	def __init__(self, gtksettings, comptonsettings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Shadows"))
		
		# State
		self.updating_shadows = False
		
		# Settings
		self.gtksettings = gtksettings
		self.comptonsettings = comptonsettings
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Window shadows
		self.window_shadows = Gtk.CheckButton(_("Enable shadows"))
		self.comptonsettings.bind(
			"shadow",
			self.window_shadows,
			"active"
		)
		
		# Panel shadows
		self.panel_shadows = Gtk.CheckButton(_("Display shadows in the panel"))
		self.comptonsettings.bind_with_convert(
			"no-dock-shadow",
			self.panel_shadows,
			"active",
			lambda x: not x,
			lambda x: not x
		)
		
		# Shadow color
		self.shadow_color_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.shadow_color_label = Gtk.Label(_("Shadow color"))
		self.shadow_color_label.set_alignment(0, 0.50)
		self.shadow_color_button = Gtk.ColorButton()
		self.shadow_color_container.pack_start(self.shadow_color_label, True, True, 0)
		self.shadow_color_container.pack_start(self.shadow_color_button, False, False, 0)
		
		self.shadow_color_button.connect("color-set", self.store_shadow_color)
		
		self.comptonsettings.connect("changed::shadow-red", self.update_shadow_color)
		self.comptonsettings.connect("changed::shadow-blue", self.update_shadow_color)
		self.comptonsettings.connect("changed::shadow-green", self.update_shadow_color)
		
		# Update shadow color manually
		for color in ("shadow-red", "shadow-blue", "shadow-green"):
			self.update_shadow_color(comptonsettings, color)
		
		self.main_container.pack_start(self.window_shadows, True, True, 2)
		self.main_container.pack_start(self.panel_shadows, True, True, 2)
		self.main_container.pack_start(self.shadow_color_container, True, True, 2)
		
		# Ensure we enable options only if shadows are enabled
		for widget in (self.panel_shadows, self.shadow_color_container):
			self.window_shadows.bind_property(
				"active",
				widget,
				"sensitive",
				GObject.BindingFlags.SYNC_CREATE
			)
		
		self.get_alignment().add(self.main_container)

class FadingFrame(CommonFrame):
	"""
	The Fading Frame
	"""
	
	def on_fading_changed(self, widget):
		"""
		Fired when the fading checkbutton has been clicked.
		"""
		
		if widget.get_active():
			# Enable other options
			self.fading_openclose.set_sensitive(True)
		else:
			# Disable other options
			self.fading_openclose.set_sensitive(False)
	
	def update_shadow_color(self, settings, color):
		"""
		Fired when a shadow color has been changed in dconf.
		"""
		
		if self.updating_shadows: return
		
		value = settings.get_double(color)
		
		if color == "shadow-red":
			self.shadow_color_rgba.red = value
		elif color == "shadow-blue":
			self.shadow_color_rgba.blue = value
		elif color == "shadow-green":
			self.shadow_color_rgba.green = value
	
	def __init__(self, gtksettings, comptonsettings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Fading"))
		
		# State
		self.updating_shadows = False
		
		# Settings
		self.gtksettings = gtksettings
		self.comptonsettings = comptonsettings
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Fading
		self.fading = Gtk.CheckButton(_("Enable fading"))
		self.comptonsettings.bind(
			"fading",
			self.fading,
			"active"
		)
		
		# Fade open/close
		self.fading_openclose = Gtk.CheckButton(_("Fade windows when they're opening/closing"))
		self.comptonsettings.bind_with_convert(
			"no-fading-openclose",
			self.fading_openclose,
			"active",
			lambda x: not x,
			lambda x: not x
		)
				
		self.main_container.pack_start(self.fading, True, True, 2)
		self.main_container.pack_start(self.fading_openclose, True, True, 2)
		
		# Ensure we enable options only if fading is enabled
		self.fading.bind_property(
			"active",
			self.fading_openclose,
			"sensitive",
			GObject.BindingFlags.SYNC_CREATE
		)
		
		self.get_alignment().add(self.main_container)

class TransparencyFrame(CommonFrame):
	"""
	The Transparency Frame
	"""
	
	def on_shadows_changed(self, widget):
		"""
		Fired when the window_shadows checkbutton has been clicked.
		"""
		
		if widget.get_active():
			# Enable other options
			self.panel_shadows.set_sensitive(True)
		else:
			# Disable other options
			self.panel_shadows.set_sensitive(False)
	
	def update_shadow_color(self, settings, color):
		"""
		Fired when a shadow color has been changed in dconf.
		"""
		
		if self.updating_shadows: return
		
		value = settings.get_double(color)
		
		if color == "shadow-red":
			self.shadow_color_rgba.red = value
		elif color == "shadow-blue":
			self.shadow_color_rgba.blue = value
		elif color == "shadow-green":
			self.shadow_color_rgba.green = value
	
	def store_shadow_color(self, button):
		"""
		Stores in dconf the shadow color.
		"""
		
		self.updating_shadows = True
		
		self.comptonsettings.set_double("shadow-red", self.shadow_color_rgba.red)
		self.comptonsettings.set_double("shadow-blue", self.shadow_color_rgba.blue)
		self.comptonsettings.set_double("shadow-green", self.shadow_color_rgba.green)
		
		self.updating_shadows = False
	
	def __init__(self, gtksettings, comptonsettings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Transparency"))
		
		# State
		self.updating_shadows = False
		
		# Settings
		self.gtksettings = gtksettings
		self.comptonsettings = comptonsettings
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		# Menu opacity
		self.menu_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.menu_label = Gtk.Label(_("Menu opacity"))
		self.menu_label.set_alignment(0, 0.50)
		self.menu_scale = Gtk.Scale.new_with_range(
			Gtk.Orientation.HORIZONTAL,
			0.0,
			1.0,
			0.10
		)
		self.comptonsettings.bind(
			"menu-opacity",
			self.menu_scale.get_adjustment(),
			"value"
		)
		self.menu_scale.set_size_request(150, -1)
		self.menu_scale.set_value_pos(Gtk.PositionType.LEFT)
		self.menu_container.pack_start(self.menu_label, True, True, 0)
		self.menu_container.pack_start(self.menu_scale, False, False, 0)

		# Inactive opacity
		self.inactive_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.inactive_label = Gtk.Label(_("Inactive opacity"))
		self.inactive_label.set_alignment(0, 0.50)
		self.inactive_scale = Gtk.Scale.new_with_range(
			Gtk.Orientation.HORIZONTAL,
			0.0,
			1.0,
			0.10
		)
		self.comptonsettings.bind(
			"inactive-opacity",
			self.inactive_scale.get_adjustment(),
			"value"
		)
		self.inactive_scale.set_size_request(150, -1)
		self.inactive_scale.set_value_pos(Gtk.PositionType.LEFT)
		self.inactive_container.pack_start(self.inactive_label, True, True, 0)
		self.inactive_container.pack_start(self.inactive_scale, False, False, 0)

		# Border opacity
		self.border_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.border_label = Gtk.Label(_("Border opacity"))
		self.border_label.set_alignment(0, 0.50)
		self.border_scale = Gtk.Scale.new_with_range(
			Gtk.Orientation.HORIZONTAL,
			0.0,
			1.0,
			0.10
		)
		self.comptonsettings.bind(
			"frame-opacity",
			self.border_scale.get_adjustment(),
			"value"
		)
		self.border_scale.set_size_request(150, -1)
		self.border_scale.set_value_pos(Gtk.PositionType.LEFT)
		self.border_container.pack_start(self.border_label, True, True, 0)
		self.border_container.pack_start(self.border_scale, False, False, 0)
		
		self.main_container.pack_start(self.menu_container, True, True, 2)
		self.main_container.pack_start(self.inactive_container, True, True, 2)
		self.main_container.pack_start(self.border_container, True, True, 2)
		
		self.get_alignment().add(self.main_container)

class AdvancedFrame(CommonFrame):
	"""
	The Advanced frame.
	"""

	def string_to_id(self, model, string):
		"""
		Searches for string in the model, and returns its position.
		"""
		
		count = -1
		
		for item in model:
			count += 1
			if item[0] == string:
				return count
		
		return -1
	
	def __init__(self, gtksettings, comptonsettings):
		"""
		Initializes the frame.
		"""
		
		super().__init__(name=_("Advanced"))
		
		# Settings
		self.gtksettings = gtksettings
		self.comptonsettings = comptonsettings
		
		# Container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		# Backend
		self.backend_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.backend_label = Gtk.Label(_("Backend"))
		self.backend_label.set_alignment(0, 0.50)
		self.backend_store = Gtk.ListStore(str, str)
		self.backend_store.append(("glx", "GLX"))
		self.backend_store.append(("xrender", "XRender"))
		self.backend_combo = Gtk.ComboBox.new_with_model(self.backend_store)
		backend_renderer = Gtk.CellRendererText()
		self.backend_combo.pack_start(backend_renderer, True)
		self.backend_combo.add_attribute(backend_renderer, "text", 1)
		self.comptonsettings.bind_with_convert(
			"backend",
			self.backend_combo,
			"active",
			lambda x: self.string_to_id(self.backend_store, x),
			lambda x: self.backend_combo.get_model()[self.backend_combo.get_active_iter()][0],
		)
		self.backend_container.pack_start(self.backend_label, True, True, 0)
		self.backend_container.pack_start(self.backend_combo, False, False, 0)

		# VSync
		self.vsync_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.vsync_label = Gtk.Label("VSync")
		self.vsync_label.set_alignment(0, 0.50)
		self.vsync_store = Gtk.ListStore(str, str)
		self.vsync_store.append(("none", _("None")))
		self.vsync_store.append(("drm", "drm"))
		self.vsync_store.append(("opengl", "opengl"))
		self.vsync_store.append(("opengl-oml", "opengl-oml"))
		self.vsync_store.append(("opengl-swc", "opengl-swc"))
		self.vsync_store.append(("opengl-mswc", "opengl-mswc"))
		self.vsync_combo = Gtk.ComboBox.new_with_model(self.vsync_store)
		vsync_renderer = Gtk.CellRendererText()
		self.vsync_combo.pack_start(vsync_renderer, True)
		self.vsync_combo.add_attribute(vsync_renderer, "text", 1)
		self.comptonsettings.bind_with_convert(
			"vsync",
			self.vsync_combo,
			"active",
			lambda x: self.string_to_id(self.vsync_store, x),
			lambda x: self.vsync_combo.get_model()[self.vsync_combo.get_active_iter()][0],
		)
		self.vsync_container.pack_start(self.vsync_label, True, True, 0)
		self.vsync_container.pack_start(self.vsync_combo, False, False, 0)
		
		self.main_container.pack_start(self.backend_container, True, True, 2)
		self.main_container.pack_start(self.vsync_container, True, True, 2)

		self.get_alignment().add(self.main_container)
		
class Paranoid(Gtk.Box):
	""" The 'Effects' page. """
	
	def __init__(self, gtksettings):
		"""
		Initializes the page.
		"""
		
		super().__init__(orientation=Gtk.Orientation.VERTICAL)
		
		# Also connect to the compton settings
		comptonsettings = Settings("org.semplicelinux.vera.compton")
		
		desktop_effects_frame = DesktopEffectsFrame(gtksettings, comptonsettings)
		shadow_frame = ShadowFrame(gtksettings, comptonsettings)
		fading_frame = FadingFrame(gtksettings, comptonsettings)
		transparency_frame = TransparencyFrame(gtksettings, comptonsettings)
		advanced_frame = AdvancedFrame(gtksettings, comptonsettings)
		
		self.pack_start(desktop_effects_frame, False, False, 2)
		self.pack_start(shadow_frame, False, False, 2)
		self.pack_start(fading_frame, False, False, 2)
		self.pack_start(transparency_frame, False, False, 2)
		self.pack_start(advanced_frame, False, False, 2)
		
		# Bind compton_enable to the sensitiveness of the compton related frames
		for frame in (shadow_frame, fading_frame, transparency_frame, advanced_frame):
			desktop_effects_frame.compton_enabled.bind_property(
				"active",
				frame,
				"sensitive",
				GObject.BindingFlags.SYNC_CREATE
			)
		
		self.show_all()

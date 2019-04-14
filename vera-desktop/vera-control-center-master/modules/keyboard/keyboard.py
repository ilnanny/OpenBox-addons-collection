# -*- coding: utf-8 -*-
#
# keyboard - keyboard module for Vera Control Center
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

import subprocess

from veracc.widgets.UnlockBar import UnlockBar, ActionResponse

from keeptalking2.Keyboard import Keyboard

from gi.repository import Gtk, GObject

@quickstart.builder.from_file("./modules/keyboard/keyboard.glade")
class Scene(quickstart.scenes.BaseScene):
	"""
	Keyboard settings.
	"""
	
	events = {
		"changed": ("model_combo", ),
		"cursor-changed": ("layout_view", "variant_view"),
	}
	
	def setxkbmap(self):
		"""
		Invokes setxkbmap and sets the currently selected layout, variant
		and model.
		"""
		
		subprocess.call(
			[
				"setxkbmap",
				self.Keyboard.default_layout,
				self.Keyboard.default_variant if self.Keyboard.default_variant else "",
				"-model" if self.Keyboard.default_model else "",
				self.Keyboard.default_model if self.Keyboard.default_model else ""
			]
		)
	
	def on_model_combo_changed(self, combobox):
		"""
		Fired when the user changes the keyboard model.
		"""
		
		itr = self.objects.model_combo.get_active_iter()
		if not itr: return
		
		selected = self.objects.models.get_value(itr, 0)
		if selected == self.Keyboard.default_variant: return
		
		try:
			self.Keyboard.set(model=selected)
			self.default_model = itr
			
			self.setxkbmap()
		except:
			self.objects.model_combo.set_active_iter(self.default_model)
	
	def on_variant_view_cursor_changed(self, treeview):
		"""
		Fired when the user changes the variant.
		"""
		
		if self.building_list: return
		
		# selection
		sel = treeview.get_selection()
		if not sel: return
		
		# iter
		model, itr = sel.get_selected()
		if not itr: return
		
		selected = self.objects.variants.get_value(itr, 0)
		if selected == self.Keyboard.default_variant: return

		try:
			self.Keyboard.set(variant=selected)
			self.default_variant = itr

			self.setxkbmap()
		except:
			sel.select_iter(self.default_variant)		
	
	def on_layout_view_cursor_changed(self, treeview):
		"""
		Fired when the user changes the locale.
		"""
		
		# selection
		sel = treeview.get_selection()
		if not sel: return
		
		# iter
		model, itr = sel.get_selected()
		if not itr: return
		
		selected = self.objects.layouts.get_value(itr, 0)
		if selected == self.Keyboard.default_layout: return

		# Reset default variant
		self.default_variant = None

		try:
			self.Keyboard.set(layout=selected, variant='')
			self.default = itr
			
			self.setxkbmap()
		except:
			sel.select_iter(self.default)

		# Rebuild variant list
		GObject.idle_add(self.build_variant_list, selected)
	
	def build_variant_list(self, layout):
		"""
		Populates the variant list.
		"""
		
		self.building_list = True
				
		self.objects.variants.clear()
		
		models, layouts = self.Keyboard.supported()
		variants = layouts[layout]["variants"]
		
		for variant in variants:
			for item, key in variant.items():
				
				itr = self.objects.variants.append([item, key])
				
				# Save the default variant
				if item == self.Keyboard.default_variant:
					self.default_variant = itr
		
		# No variant
		reciter = self.objects.variants.prepend(['', layouts[layout]["description"]])
		
		sel = self.objects.variant_view.get_selection()
		if self.default_variant:
			sel.select_iter(self.default)
		else:
			# No variant, use reciter
			sel.select_iter(reciter)
		
		GObject.idle_add(self.objects.variant_view.scroll_to_cell, sel.get_selected_rows()[1][0])
		
		self.building_list = False
	
	def build_model_list(self):
		"""
		Populates the model list.
		"""
		
		pc105 = None
		
		self.objects.models.clear()
		
		models = self.Keyboard.supported()[0]
		
		for item, key in models.items():
			itr = self.objects.models.append([item, key])
			
			# Save the default model
			if item == self.Keyboard.default_model:
				self.default_model = itr
			elif item == "pc105":
				# Fallback
				pc105 = itr
		
		if self.default_model:
			self.objects.model_combo.set_active_iter(self.default_model)
		else:
			self.objects.model_combo.set_active_iter(pc105)

	
	def build_layout_list(self):
		"""
		Populates the layout list.
		"""
		
		self.objects.layouts.clear()
		
		models, layouts = self.Keyboard.supported()
		
		for item, key in layouts.items():
			itr = self.objects.layouts.append([item, key["description"]])
			
			# Save iter if it's the default...
			if item == self.Keyboard.default_layout:
				self.default = itr
		
		if self.default:
			sel = self.objects.layout_view.get_selection()
			sel.select_iter(self.default)
						
			GObject.idle_add(self.objects.layout_view.scroll_to_cell, sel.get_selected_rows()[1][0])
			
			# Also build the variant view!
			GObject.idle_add(self.build_variant_list, self.Keyboard.default_layout)
	
	def on_locked(self, unlockbar):
		"""
		Fired when the scene has been locked.
		"""
		
		GObject.idle_add(self.objects.content.set_sensitive, False)
	
	def on_unlocked(self, unlockbar):
		"""
		Fired when the scene has been unlocked.
		"""
		
		GObject.idle_add(self.objects.content.set_sensitive, True)
	
	def prepare_scene(self):
		""" Called when doing the scene setup. """
		
		self.scene_container = self.objects.main
		
		# Create unlockbar
		self.unlockbar = UnlockBar("org.freedesktop.locale1.set-keyboard")
		self.unlockbar.connect("locked", self.on_locked)
		self.unlockbar.connect("unlocked", self.on_unlocked)
		self.objects.main.pack_start(self.unlockbar, False, False, 0)		

		self.Keyboard = Keyboard()
		
		self.building_list = False
		
		self.default = None
		self.default_variant = None
		self.default_model = None

		# Make the layout_view treeview working...
		layout_renderer = Gtk.CellRendererText()
		self.layout_column = Gtk.TreeViewColumn("Layout", layout_renderer, text=1)
		self.objects.layouts.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		self.objects.layout_view.append_column(self.layout_column)
		
		# Do the same for the variant_view...
		variant_renderer = Gtk.CellRendererText()
		self.variant_column = Gtk.TreeViewColumn("Variant", variant_renderer, text=1)
		self.objects.variants.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		self.objects.variant_view.append_column(self.variant_column)
		
		# And something similar for the model combobox...
		model_renderer = Gtk.CellRendererText()
		self.objects.model_combo.pack_start(model_renderer, True)
		self.objects.model_combo.add_attribute(model_renderer, "text", 1)
		self.objects.models.set_sort_column_id(1, Gtk.SortType.ASCENDING)

		# Populate the layout list
		GObject.idle_add(self.build_layout_list)
		
		# Populate the model list
		GObject.idle_add(self.build_model_list)
	
	def on_scene_called(self):
		"""
		Show the scene!
		"""
		
		# We are locked
		self.unlockbar.emit("locked")

	def on_scene_asked_to_close(self):
		"""
		Do some cleanup before returning home
		"""
		
		self.unlockbar.cancel_authorization()
				
		return True

#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# vera-control-center - Vera Control Center
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

import veracc.module

from veracc.widgets.SectionFrame import SectionFrame

from gi.repository import Gtk, Gdk, Gio, GObject
from gi.repository.GdkPixbuf import Pixbuf

from collections import OrderedDict

import quickstart

import subprocess

if os.path.islink(__file__):
	# If we are a link, everything is a WTF...
	VERACC_DIR = os.path.dirname(os.path.normpath(os.path.join(os.path.dirname(__file__), os.readlink(__file__))))
else:
	VERACC_DIR = os.path.dirname(__file__)

MODULES_DIR = os.path.join(VERACC_DIR, "modules/")
MODULES_PREFIX = "modules"

# Translations
TRANSLATION = quickstart.translations.Translation("vera-control-center")
TRANSLATION.load()
TRANSLATION.install()
TRANSLATION.bind_also_locale()

SECTIONS = OrderedDict([
	("Personal", _("Personal")),
	("System", _("System")),
	("Network", _("Network")),
	("Hardware", _("Hardware"))
])

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 600

# While the following is not ideal, is currently needed to make sure
# we are actually on the main vera-control-center directory.
# The main executable (this) and all modules do not use absolute paths
# to load the glade UI files, so we need to be on the main directory
# otherwise they will crash.
# This should be probably addressed directly in quickstart.builder but,
# for now, this chdir call will do the job.
os.chdir(VERACC_DIR)

@quickstart.style.custom_css("./veracc.css")
@quickstart.builder.from_file("./controlcenterui.glade")
class ControlCenter:
	""" Main Interface """
	
	scenes = {
		"home":":VeraCChome",
	}
	
	events = {
		"destroy": ("main",),
		"clicked": ("back_button",),
		"search-changed" : ("searchbox",),
	}
	
	# Modules (ordered)dict
	modules = OrderedDict()
	
	# This is the scenes container
	scene_container = Gtk.Stack()
	
	# This is the VBox where all SectionFrames are packed...
	section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	
	def reset_window_details(self):
		"""
		Resets the window details.
		"""
		
		self.objects.main.set_title(_("Settings"))
		self.objects.main.set_icon_name("preferences-system")
		
		# An external module may have changed the translations binding,
		# so restore ours
		TRANSLATION.bind_also_locale()
	
	def change_window_details(self, liststore, giter):
		"""
		Changes the details of the window using the
		informations of the given iter.
		"""
		
		self.objects.main.set_title(liststore.get_value(giter, 1))
		self.objects.main.set_icon_name(liststore.get_value(giter, 6))
	
	def on_back_button_clicked(self, button):
		""" Called when the back button has been clicked. """
		
		if self.scene_manager.current_scene != "home" and self.scene_manager.can_close():
			self.scene_manager.load("home")
			
			# Reset details
			self.reset_window_details()
			
			# Hide the back button
			self.objects.back_button.hide()
	
	def on_searchbox_search_changed(self, box):
		"""
		Fired when the searchbox has been changed.
		"""
		
		self.objects.back_button.emit("clicked")
		
		for section in self.section_box.get_children():
			section.search(box.get_text().lower())
	
	def on_main_destroy(self, window):
		""" Called when destroying window. """
		
		Gtk.main_quit()
	
	def on_item_selected(self, iconview, path):
		"""
		Called when an item has been selected.
		"""
		
		# Unselect everything in the iconview
		iconview.unselect_all()
		
		# Now finally load the module
		store = iconview.get_model()
		giter = store.get_iter(path)
		
		# Check if the module is external.
		# path[5] is the boolean value that we should check
		if store.get_value(giter, 5):
			# It is external, just ask our friend subprocess to handle
			# the thing
			# path[4] houses the command to execute
			subprocess.Popen(store.get_value(giter, 4), shell=True)
		else:
			# Internal module, awesome!
			
			# Ensure the back button is always shown
			self.objects.back_button.show()
			
			# Ensure the window is scrolled to the top
			self.objects.scroll.get_vadjustment().set_value(0.0)
			
			# Load.
			# path[3] is the module name.
			self.scene_manager.load(store.get_value(giter, 3))

			# Change details
			self.change_window_details(store, giter)
			
	def detect_modules(self):
		"""
		Detects modules.
		"""
		
		for module in os.listdir(MODULES_DIR):
			if module in ("__pycache__", "__init__.py"):
				continue
			
			#print("Detected %s" % module)
			
			mod = veracc.module.VeraCCModule(module, os.path.join(MODULES_DIR, module))
			
			if not mod.launcher_section in self.modules:
				self.modules[mod.launcher_section] = []
			self.modules[mod.launcher_section].append(mod)
			
			# Also append to the scenes dictionary
			if not mod.module_is_external:
				self.scenes[module] = "%s.%s.%s" % (MODULES_PREFIX, module, module)
		
		# Create SectionFrames and populate them
		custom_sections = [ x for x in self.modules.keys() if x not in SECTIONS ]	
		for section in list(SECTIONS.keys()) + custom_sections:
			
			if not section in self.modules:
				continue
			
			lst = self.modules[section]
			
			sf = SectionFrame(SECTIONS[section] if section in SECTIONS else section)
			sf.populate(lst)
			
			# Connect the internal iconview to our global handler
			sf.iconview.connect("item-activated", self.on_item_selected)
			
			self.section_box.pack_start(sf, False, False, 0)
	
	def __init__(self):
		""" Initialize the interface """
		
		# Create the scene manager
		self.scene_manager = quickstart.scenes.initialize(self)
		
		# Resize, taking in account eventual lower resolutions
		current_width = Gdk.Screen.width()
		current_height = Gdk.Screen.height()
		self.objects.main.set_size_request(
			WINDOW_WIDTH if current_width > WINDOW_WIDTH else current_width-10,
			WINDOW_HEIGHT if current_height > WINDOW_HEIGHT else current_height-70 # should take into account panel and titlebar
		)
				
		# Setup the scene container
		#self.scene_container.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		self.scene_container.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.scene_container.set_homogeneous(False)
		
		self.objects.viewport.add(self.scene_container)
		
		# Create the main page
		eventbox = Gtk.EventBox()
		alignment = Gtk.Alignment()
		alignment.set_padding(5, 5, 5, 5)
		alignment.add(self.section_box)
		eventbox.add(alignment)
		
		# We want to achieve the look of an "entire" iconview, so
		# we make the entire eventbox a 'view'
		eventbox.get_style_context().add_class("view")
		
		self.scene_container.add_named(eventbox, "VeraCChome")
		self.scene_manager.load("home")
		
		# Do detections...
		self.detect_modules()
		
		# Finally, show the window
		self.objects.main.show_all()

		# ...hide the back button
		self.objects.back_button.hide()
		
		# ...and focus the searchbox!
		self.objects.searchbox.grab_focus()

quickstart.common.quickstart(ControlCenter)

# -*- coding: utf-8 -*-
#
# tint panel config module - Simple GUI to tweak the panel
# Copyright (C) 2013  Eugenio "g7" Paolantonio
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
#
# This module is based on tint2-panel-config, see semplice/tint2-panel-config
# @ GitHub.

from gi.repository import Gtk, GMenu, GObject, Gio
import quickstart
import os
import xdg.DesktopEntry

from veracc.widgets.ApplicationSelectionDialog import ApplicationSelectionDialog

CONFIG = os.path.expanduser("~/.config/tint2/secondary_config")

#tr = quickstart.translations.Translation("tint2-panel-config")
#tr.install()
#tr.bind_also_locale()

position_dict = {
	"top" : 0,
	"center" : 1,
	"bottom" : 2
}

@quickstart.builder.from_file("./modules/tint2/tint2.glade")
class Scene(quickstart.scenes.BaseScene):
	
	application_selection_dialog = None
	
	events = {
		"destroy" : (
			"main",
		),
		"toggled" : (
			"enabled_checkbox",
		),
		"clicked" : (
			"add_button",
			"remove_button",
		),
		"cursor-changed" : (
			"enabled_treeview",
		),
		"changed" : (
			"position_combo",
		)
	}

	def on_enabled_treeview_cursor_changed(self, treeview):
		""" Fired when the user changed something on the enabled_treeview. """
		
		# Enable remove button
		GObject.idle_add(self.objects["remove_button"].set_sensitive, True)

	def on_add_button_clicked(self, button):
		""" Fired when the Add launcher button has been clicked. """
				
		if not self.application_selection_dialog:
			self.application_selection_dialog = ApplicationSelectionDialog()
			self.application_selection_dialog.build_application_list()
			
			# Connect response signal
			self.application_selection_dialog.connect("response", self.on_application_selection_dialog_response)
			
			# Bind sensitiveness of the parent with the visibility of the new window
			self.application_selection_dialog.bind_property(
				"visible",
				self.objects["main"],
				"sensitive",
				GObject.BindingFlags.INVERT_BOOLEAN
			)
		
		self.application_selection_dialog.show()
		
	
	def on_remove_button_clicked(self, button):
		""" Fired when the Remove launcher button has been clicked. """
		
		# Get selection
		selection = self.objects["enabled_treeview"].get_selection()
		model, treeiter = selection.get_selected()
		
		del model[treeiter]
		
		# Disable remove button if we should
		if len(model) == 0: GObject.idle_add(self.objects["remove_button"].set_sensitive, False)
	
	def on_application_selection_dialog_response(self, dialog, response_id):
		"""
		Fired when the user triggered a response on the application_selection_dialog.
		"""
		
		# Hide
		dialog.hide()
		
		if response_id in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
			return
		
		# Get and add selection
		self.enabled_model.append(dialog.get_selection())

	
	def on_scene_asked_to_close(self):
		""" Fired when the back button has been pressed """
		
		settings = Gtk.Settings.get_default()
		icon_theme = settings.get_property("gtk-icon-theme-name")
		
		if not os.path.exists(os.path.dirname(CONFIG)):
			os.makedirs(os.path.dirname(CONFIG))
		
		with open(CONFIG, "w") as f:
			if self.objects["position_combo"].get_active() != position_dict["bottom"]:
				# Panel position. If it is Bottom do not save it.
				# This avoids messing up with the panel position for those
				# who already modified it in the *primary* config.
				f.write("panel_position = %s left horizontal\n" % self.objects["combostore"][self.objects["position_combo"].get_active_iter()][1])
				
				# Ensure that windows can be on top of the panel if the position is top
				if self.objects["position_combo"].get_active() == position_dict["top"]:
					f.write("panel_layer = bottom\n")
			if self.objects["Hide_checkbox"].get_active():
				f.write("autohide = 1\n")
				
			if self.objects["ampm_enabled"].get_active():
				f.write("time1_format = %I:%M %p\n")
				
			if self.objects["enabled_checkbox"].get_active():
				f.write("panel_items = LTSC\n")
			else:
				f.write("panel_items = TSC\n")
				
			f.write("launcher_icon_theme = %s\n" % icon_theme)
			
			for treeiter in self.enabled_model:
				f.write("launcher_item_app = %s\n" % treeiter[1])				
			
			if self.objects["inverted_scroll_actions"].get_active():
				f.write("mouse_scroll_down = toggle\nmouse_scroll_up = iconify\n")
		
		os.system("killall -SIGUSR1 tint2")
		
		# Destroy application_selection_dialog
		if self.application_selection_dialog:
			self.application_selection_dialog.destroy()
			self.application_selection_dialog = None
		
		return True
	
	def on_main_destroy(self, window):
		""" Fired when the main window should be destroyed. """
		
		Gtk.main_quit()
	
	def on_enabled_checkbox_toggled(self, checkbox):
		""" Fired when the enabled checkbox has been toggled. """
		
		if checkbox.get_active():
			GObject.idle_add(self.objects["enabled_box"].set_sensitive, True)
			GObject.idle_add(self.objects["add_button"].set_sensitive, True)
		else:
			GObject.idle_add(self.objects["enabled_box"].set_sensitive, False)
	
	def on_position_combo_changed(self, combo):
		""" Fired when the position combobox has been changed. """
		
		# Pre-set "Invert mouse scroll actions" if the newly selected
		# position is Top.
		if self.objects["position_combo"].get_active() == position_dict["top"]:
			self.objects["inverted_scroll_actions"].set_active(True)
		else:
			self.objects["inverted_scroll_actions"].set_active(False)
	
	@quickstart.threads.thread
	def initialize(self):
		""" Builds the enabled list. """
		
		# Set-up the enabled_treeview
		self.enabled_model = Gtk.ListStore(str, str, Gio.Icon)
		# Link the treeview
		self.objects["enabled_treeview"].set_model(self.enabled_model)
		
		# Column
		column = Gtk.TreeViewColumn("Everything")
		
		# Icon
		cell_icon = Gtk.CellRendererPixbuf()
		column.pack_start(cell_icon, False)
		column.add_attribute(cell_icon, "gicon", 2)

		# Text
		cell_text = Gtk.CellRendererText()
		column.pack_start(cell_text, False)
		column.add_attribute(cell_text, "text", 0)
		
		# Append
		self.objects["enabled_treeview"].append_column(column)

		# Position combo: create renderer
		cellrenderer = Gtk.CellRendererText()
		self.objects["position_combo"].pack_start(cellrenderer, True)
		self.objects["position_combo"].add_attribute(cellrenderer, "text", 0)

		# Default position is "Bottom" (will be overriden later if we need to)
		self.objects["position_combo"].set_active(position_dict["bottom"])

		# Open config
		if os.path.exists(CONFIG):
			
			up_inverted = False
			down_inverted = False
			
			with open(CONFIG) as f:
				for line in f.readlines():
					try:
						line = line.split("=")
						if line[0].startswith("launcher_item_app"):
							# A launcher!
							path = line[1].strip("\n").replace(" /","/",1)
							desktopentry = xdg.DesktopEntry.DesktopEntry(path)
							iconpath = desktopentry.getIcon()
							if iconpath and iconpath.startswith("/"):
								icon = Gio.Icon.new_for_string(iconpath)
							elif iconpath:
								icon = Gio.ThemedIcon.new(iconpath.replace(".png",""))
							else:
								icon = None
							self.enabled_model.append((desktopentry.getName(), path, icon))
						elif line[0].startswith("panel_items"):
							# Is the launcher enabled or not?
							if "L" in line[1]:
								# YES!
								self.objects["enabled_checkbox"].set_active(True)
							else:
								# No :/
								GObject.idle_add(self.objects["enabled_box"].set_sensitive, False)
						elif line[0].startswith("time1_format"):
							# AM/PM?
							if "%p" in line[1]:
								# Yes!
								self.objects["ampm_enabled"].set_active(True)
							else:
								# No
								self.objects["ampm_enabled"].set_active(False)
						elif line[0].startswith("autohide"):
							# Autohide?
							if "1" in line[1]:
								# Yes
								self.objects["Hide_checkbox"].set_active(True)
							else:
								# No
								self.objects["Hide_checkbox"].set_active(False)
						elif line[0].startswith("panel_position"):
							# Position
							splt = line[1].strip("\n").split(" ")
							while splt.count(""):
								splt.remove("")
							self.objects["position_combo"].set_active(position_dict[splt[0]])
						elif line[0].startswith("mouse_scroll_"):
							# Mouse scroll (up/down) actions.
							# Usually if they are on the secondary_config
							# it's because they're inverted, but let's check
							# anyways...
							if "down" in line[0] and "toggle" in line[1]:
								down_inverted = True
							elif "up" in line[0] and "iconify" in line[1]:
								up_inverted = True
					except Exception:
						print("Error while loading configuration.")
			
			self.objects["inverted_scroll_actions"].set_active(down_inverted and up_inverted)

		else:
			# Ensure the enabled_checkbox is not active.
			self.objects["enabled_checkbox"].set_active(False)
			self.objects["add_button"].set_sensitive(False)

		# First start, disable remove button.
		GObject.idle_add(self.objects["remove_button"].set_sensitive, False)
	
	def prepare_scene(self):
		""" Called when doing the scene setup. """
		
		self.scene_container = self.objects.main
		
		self.initialize()
		
		self.objects["main"].show_all()
		

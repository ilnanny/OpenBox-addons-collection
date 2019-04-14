# -*- coding: utf-8 -*-
#
# autostart - autostart management module for Vera Control Center
# Copyright (C) 2014  Eugenio "g7" Paolantonio <me@medesimo.eu>
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

# This module is only "one-way", so it doesn't react to events from the
# outside (i.e. changes made via dconf-editor).
# We do not bind anything here, so we keep everything simple by
# not implementing "two-way" syncronization of settings.
# If you change something via another application while vera-control-center
# (and this module) is open, you should close and reopen the control center
# again. 

import os

import shutil

import random

import quickstart

from gi.repository import Gtk, GdkPixbuf, GObject, Gio

from xdg.DesktopEntry import DesktopEntry

from veracc.utils import Settings

from veracc.widgets.ApplicationSelectionDialog import ApplicationSelectionDialog

# Search path for the applications.
#
# /usr/share/vera/autostart is taken out volountairly because it contains
# core applications that the user doesn't want to disable.
# You can still disable those by manually modifying the vera settings via
# e.g. dconf-editor.
SEARCH_PATH = (
	"/etc/xdg/autostart",
	os.path.expanduser("~/.config/autostart")
)

# dconf settings
SETTINGS = Settings("org.semplicelinux.vera")

# Blacklist
BLACKLIST = SETTINGS.get_strv("autostart-ignore")

class ApplicationRow(Gtk.ListBoxRow):
	
	"""
	An ApplicationRow is a modified Gtk.ListBoxRow that shows informations
	about an application to autostart.
	It permits to enable or disable the application via a Switch.
	
	--------------------------------------------------------------------
	|  ICON   Program name                                       ##ON  |
	--------------------------------------------------------------------
	"""
	
	__gsignals__ = {
		"changed" : (
			GObject.SIGNAL_RUN_LAST,
			None,
			(str, bool)
		),
		"requests-edit" : (
			GObject.SIGNAL_RUN_LAST,
			None,
			(object,)
		),
	}
	
	def reset_default(self):
		"""
		Resets the default value of the application (Enabled/Disabled)
		"""
		
		self.switch.set_active(not (self.base_name in BLACKLIST))
	
	def __init__(self, base_name, application_desktop):
		"""
		Inititializes the Row.
		
		base_name is the basename of the desktop file used to obtain
		application_desktop.
		
		application_desktop is the xdg.DesktopEntry of the application
		to show.
		"""
		
		super().__init__()
		
		self.base_name = base_name
		self.application_desktop = application_desktop
		
		# Main container
		self.main_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		
		# Icon
		self.icon = Gtk.Image()
		
		# Label (name)
		self.name = Gtk.Label()
		self.name.set_alignment(0, 0.5)
		
		# Switch
		self.switch = Gtk.Switch()
		
		# Edit button
		self.edit = Gtk.Button.new_from_icon_name("edit-symbolic", Gtk.IconSize.BUTTON)
		self.edit.set_always_show_image(True)
		
		# Add to container
		self.main_container.pack_start(self.icon, False, False, 2)
		self.main_container.pack_start(self.name, True, True, 2)
		self.main_container.pack_start(self.edit, False, False, 2)
		self.main_container.pack_start(self.switch, False, False, 2)
		
		# Populate using informations from the DesktopEntry
		icon = self.application_desktop.getIcon()
		if icon.startswith("/"):
			# Path to icon
			#
			# We could use set_from_file here but then we don't have
			# control of the resulting image size, so we are fallbacking
			# to a Pixbuf.
			self.icon.set_from_pixbuf(
				GdkPixbuf.Pixbuf.new_from_file_at_scale(
					icon,
					24,
					24,
					True
				)
			)
		else:
			# Icon name
			self.icon.set_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR) # 24px
		
		self.name.set_text(self.application_desktop.getName())
		
		# Value
		self.reset_default()
		
		# Connect the switch and edit button
		self.switch.connect(
			"notify::active",
			lambda x, y: self.emit("changed", self.base_name, x.get_active())
		)
		
		# Check for writeability of the desktop file, and disable the edit
		# button if the file is not writeable
		if not os.access(self.application_desktop.filename, os.W_OK):
			self.edit.set_sensitive(False)
			self.edit.set_tooltip_text(_("You don't have enough permissions to edit or remove «%s»") % self.application_desktop.getName())
		else:
			# Create connection
			self.edit.connect(
				"clicked",
				lambda x: self.emit("requests_edit", self.application_desktop)
			)
			self.edit.set_tooltip_text(_("Edit or remove «%s»") % self.application_desktop.getName())
		
		# Finally add the container to the row
		self.add(self.main_container)
		self.show_all()

@quickstart.builder.from_file("./modules/autostart/autostart.glade")
class Scene(quickstart.scenes.BaseScene):
	"""
	The main scene.
	"""
	
	events = {
		"response": ("add_new_custom_dialog",), # the application selection dialog is handled manually
		"delete-event" : ("add_new_custom_dialog",),
		"changed" : ("custom_name", "custom_command",),
	}
	
	application_selection_dialog = None
	
	desktop_list = []
	
	current_edit_informations = {}
	
	def on_custom_entry_changed(self, entry):
		"""
		Fired when a custom entry has been changed.
		This method isn't directly connected to the custom GtkEntries, but it's
		directly linked to the on_custom_<id>_changed methods that quickstart
		expects.
		"""
		
		self.objects.add_new_custom_dialog.get_widget_for_response(Gtk.ResponseType.OK).set_sensitive(
			not (
				(
					self.objects.custom_name.get_text_length() == 0
				) or (
					self.objects.custom_command.get_text_length() == 0
				)
			)
		)
	
	on_custom_name_changed = on_custom_entry_changed
	on_custom_command_changed = on_custom_entry_changed
	
	def on_application_selection_dialog_response(self, dialog, response_id):
		"""
		Fired when the user triggered a response on the application_selection_dialog.
		"""
		
		# Hide
		dialog.hide()

		if response_id in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
			return
		
		# Get selection
		desktop_file = dialog.get_selection()[1]
		desktop_basename = os.path.basename(desktop_file)
		
		if os.path.basename(desktop_file) in self.desktop_list:
			# Already in list, bye
			return
		
		# Copy the desktop file and prepend a new row.
		# FIXME: currently applications with KDE in "OnlyShowIn" will get
		# regularly added, but they won't be autostarted by vera and they
		# will not show again on this module.
		#
		# This can be resolved once vera supports a "force-list", see
		# https://github.com/vera-desktop/vera/issues/2
		
		# Copy the desktop file to ~/.config/autostart
		directory = os.path.expanduser("~/.config/autostart")
		target_file = os.path.join(directory, desktop_basename)
		if not os.path.exists(directory):
			os.makedirs(directory)
		shutil.copy2(
			desktop_file,
			target_file
		)

		entry = DesktopEntry(target_file)
		
		row = ApplicationRow(desktop_basename, entry)
		
		# Connect the changed signal
		row.connect("changed", self.on_row_changed)
		
		# Connect the requests_edit signal
		row.connect("requests_edit", self.on_row_requests_edit)
		
		# Prepend the row
		self.objects.list.prepend(row)
		
		self.desktop_list.append(desktop_basename)
	
	def on_add_new_application_activated(self, menuitem, parameter):
		"""
		Fired when the add new application item has been selected.
		"""

		if not self.application_selection_dialog:
			self.application_selection_dialog = ApplicationSelectionDialog()
			self.application_selection_dialog.build_application_list()
			
			# Connect response signal
			self.application_selection_dialog.connect("response", self.on_application_selection_dialog_response)

			# Bind sensitiveness of the parent with the visibility of the new window
			self.application_selection_dialog.bind_property(
				"visible",
				self.objects.main,
				"sensitive",
				GObject.BindingFlags.INVERT_BOOLEAN
			)
		
		self.application_selection_dialog.show()
	
	def on_add_new_custom_activated(self, menuitem, parameter):
		"""
		Fired when the add new custom application item has been selected.
		"""
		
		# Set the proper title
		self.objects.add_new_custom_dialog.set_title(_("Add a new custom command"))
		
		# Hide the Remove button
		self.objects.add_new_custom_dialog.get_widget_for_response(Gtk.ResponseType.NO).hide()
		
		# Disable the sensitiveness of the Select button
		self.objects.add_new_custom_dialog.get_widget_for_response(Gtk.ResponseType.OK).set_sensitive(False)
		
		# Grab focus on the custom_name entry
		self.objects.custom_name.grab_focus()
		
		# Show the add_new_custom dialog
		self.objects.add_new_custom_dialog.show()

	def on_row_requests_edit(self, row, application_desktop):
		"""
		Fired when the add new custom application item has been selected.
		"""
		
		# Set the proper title
		self.objects.add_new_custom_dialog.set_title(_("Edit application"))
		
		# Show the Remove button
		self.objects.add_new_custom_dialog.get_widget_for_response(Gtk.ResponseType.NO).show()
		
		# Disable the sensitiveness of the Select button
		self.objects.add_new_custom_dialog.get_widget_for_response(Gtk.ResponseType.OK).set_sensitive(False)
		
		# Grab focus on the custom_name entry
		self.objects.custom_name.grab_focus()

		# Preload Name and Exec
		self.objects.custom_name.set_text(application_desktop.getName())
		self.objects.custom_command.set_text(application_desktop.getExec())
		
		# Populate self.current_edit_informations
		self.current_edit_informations["row"] = row
		self.current_edit_informations["desktop"] = application_desktop
		
		# Show the add_new_custom dialog
		self.objects.add_new_custom_dialog.show()
	
	def on_add_new_custom_dialog_response(self, dialog, response_id):
		"""
		Fired when the user triggered a response on the add_new_custom_dialog.
		"""
		
		# Clunky way to see if we have edit mode, but it works
		on_edit = dialog.get_widget_for_response(Gtk.ResponseType.NO).props.visible
		
		if not on_edit and response_id == Gtk.ResponseType.OK:
			# Obtain a working filename
			directory = os.path.expanduser("~/.config/autostart")
			if not os.path.exists(directory):
				os.makedirs(directory)
			
			filename = os.path.join(
				directory,
				self.objects.custom_name.get_text().lower().replace(" ","-") + ".custom%s.desktop" %
					(random.randint(0,1000),)
			)
			if os.path.exists(filename):
				return on_add_new_custom_dialog_response(dialog, response_id)
			
			desktop_basename = os.path.basename(filename)
			
			entry = DesktopEntry(filename)
			entry.set("Version", 1.0)
			entry.set("Name", self.objects.custom_name.get_text())
			entry.set("Exec", self.objects.custom_command.get_text())
			entry.set("X-Vera-Autostart-Phase", "Other")
			entry.write()
			
			row = ApplicationRow(desktop_basename, entry)
			
			# Connect the changed signal
			row.connect("changed", self.on_row_changed)

			# Connect the requests_edit signal
			row.connect("requests_edit", self.on_row_requests_edit)
			
			# Prepend the row
			self.objects.list.prepend(row)
			
			self.desktop_list.append(desktop_basename)
		elif on_edit and response_id == Gtk.ResponseType.OK:
			# Edit
			
			self.current_edit_informations["desktop"].set("Name", self.objects.custom_name.get_text(), locale=True)
			self.current_edit_informations["desktop"].set("Exec", self.objects.custom_command.get_text())
			self.current_edit_informations["desktop"].write()
			
			self.current_edit_informations["row"].name.set_text(self.objects.custom_name.get_text())
		elif on_edit and response_id == Gtk.ResponseType.NO:
			# Remove
			
			# Cleanup the entry from the ignore list by ensuring that
			# it's enabled in its last moments...
			self.on_row_changed(
				self.current_edit_informations["row"],
				os.path.basename(self.current_edit_informations["desktop"].filename),
				True
			)
			
			# Finally, remove
			os.remove(self.current_edit_informations["desktop"].filename)
			self.current_edit_informations["row"].destroy()
		
		# Hide
		dialog.hide()
		
		# Cleanup
		self.objects.custom_name.set_text("")
		self.objects.custom_command.set_text("")
		self.current_edit_informations = {}
	
	def on_add_new_custom_dialog_delete_event(self, dialog, event):
		"""
		Fired when the delete-event event of the add_new_custom_dialog is emitted.
		"""
		
		# Do not destroy
		return True
	
	def on_row_changed(self, row, application, enabled):
		"""
		Fired when the switch of a row has been modified.
		"""
		
		if enabled and application in BLACKLIST:
			# Remove from the blacklist
			BLACKLIST.remove(application)
		elif not enabled and application not in BLACKLIST:
			# Add to the blacklist
			BLACKLIST.append(application)
		
		# Set the new array
		SETTINGS.set_strv("autostart-ignore", BLACKLIST)
	
	#@quickstart.threads.on_idle
	@quickstart.threads.thread
	def add_applications(self):
		"""
		Populates the self.objects.list ListBox with the applications
		in SEARCH_PATH.
		"""
		
		for path in SEARCH_PATH:
			
			if not os.path.exists(path): continue
			
			for application in os.listdir(path):
				
				# Add the application, if we can
				try:
					entry = DesktopEntry(os.path.join(path, application))
					if not "KDE" in entry.getOnlyShowIn() and not application in self.desktop_list:
						
						# While excluding only KDE is not ideal, we do so
						# to have consistency with vera's AutostartManager.
						# This check is obviously a FIXME.
						
						row = ApplicationRow(application, entry)
						
						# Connect the changed signal
						row.connect("changed", self.on_row_changed)
						
						# Connect the requests_edit signal
						row.connect("requests_edit", self.on_row_requests_edit)
						
						GObject.idle_add(self.objects.list.insert,
							row,
							-1
						)
						
						self.desktop_list.append(application)
				except:
					print("Unable to show informations for %s." % application)
	
	def prepare_scene(self):
		"""
		Scene setup.
		"""
				
		self.scene_container = self.objects.main
		
		# Create menu
		actiongroup = Gio.SimpleActionGroup.new()
		
		menu = Gio.Menu()
		menu.append(
			_("Select..."),
			"add-new.application"
		)
		menu.append(
			_("Use a custom command"),
			"add-new.custom"
		)
		
		add_new_application = Gio.SimpleAction.new("application", None)
		add_new_application.connect("activate", self.on_add_new_application_activated)
		
		add_new_custom = Gio.SimpleAction.new("custom", None)
		add_new_custom.connect("activate", self.on_add_new_custom_activated)
		
		actiongroup.add_action(add_new_application)
		actiongroup.add_action(add_new_custom)
		
		# Create popover
		self.popover = Gtk.Popover.new_from_model(self.objects.add_new, menu)
		self.popover.set_position(Gtk.PositionType.BOTTOM)
		self.popover.insert_action_group("add-new", actiongroup)

		self.objects.add_new.set_popover(self.popover)
		
		# Set-up the add_new_custom_dialog
		self.objects.add_new_custom_dialog.add_buttons(
			_("_Remove"), Gtk.ResponseType.NO,
			_("_Cancel"), Gtk.ResponseType.CANCEL,
			_("_Save"), Gtk.ResponseType.OK
		)

		# Bind sensitiveness of the parent with the visibility of the new window
		self.objects.add_new_custom_dialog.bind_property(
			"visible",
			self.objects.main,
			"sensitive",
			GObject.BindingFlags.INVERT_BOOLEAN
		)

		# Make the Select button the default
		self.objects.add_new_custom_dialog.set_default_response(Gtk.ResponseType.OK)
		
		# Set destructive-action to the Remove button
		self.objects.add_new_custom_dialog.get_widget_for_response(Gtk.ResponseType.NO).get_style_context().add_class("destructive-action")
		
		self.add_applications()
	
	def on_scene_asked_to_close(self):
		"""
		Cleanup
		"""
		
		if self.application_selection_dialog:
			self.application_selection_dialog.destroy()
			self.application_selection_dialog = None
		
		return True
		

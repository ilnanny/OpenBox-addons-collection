# -*- coding: utf-8 -*-
#
# usersadmin - User and groups management
# Copyright (C) 2015  Eugenio "g7" Paolantonio <me@medesimo.eu>
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

from veracc.widgets.UnlockBar import UnlockBar, ActionResponse

from .widgets import AddNewBox, UserBox

from gi.repository import Gio, GObject, Gtk

BUS_NAME = "org.semplicelinux.usersd"
USER_IFACE = "org.semplicelinux.usersd.user"

CURRENT_UID = os.getuid()

NO_FULLNAME_STRING = _("<i>Click the edit button to set the full name</i>")

# These are the default groups for newly-created users.
# These groups have been fine-grained for Desktop users and purely on
# their convenience merits.
#
# To ensure better security and control in the future these "Privilegies"
# will be asked before actually creating the user.
DEFAULT_GROUPS = [
	'dialout',
	'lp',
	'scanner',
	'fax',
	'video',
	'fuse',
	'netdev',
	'dip',
	'floppy',
	'cdrom',
	'tape',
	'plugdev',
	'audio'
]

@quickstart.builder.from_file("./modules/usersadmin/usersadmin.glade")
class Scene(quickstart.scenes.BaseScene):
	""" Desktop preferences. """
	
	events = {
		"clicked": (
			"change_fullname_button",
			"change_password_button",
			"change_groups_button",
			"delete_user_button",
		),
		"response": (
			"delete_user_dialog",
			"groups_dialog",
		),
		"delete-event": (
			"delete_user_dialog",
			"groups_dialog",
		),
		"row_selected": ("user_list",),
	}
	
	on_edit_mode = False
	
	current_user = None
	current_user_properties = None
	current_user_box = None
	caller_user_box = None
	
	def handle_delete_events(self, window, event):
		"""
		Handles a dialog delete-event.
		"""
		
		return True
	
	on_delete_user_dialog_delete_event = on_groups_dialog_delete_event = handle_delete_events
	
	def on_locked(self, unlockbar):
		"""
		Fired when the Polkit auth has been revoked.
		"""
		
		# Switch again to the caller user
		self.objects.user_list.select_row(self.caller_user_box)
	
	def on_unlocked(self, unlockbar):
		"""
		Fired when the Polkit auth has been given.
		"""
		
		pass
	
	@quickstart.threads.on_idle
	def restore_edit_mode(self):
		"""
		Restores the full "edit" mode on the user details part.
		"""
		
		self.objects.fullname.show()
		self.objects.new_fullname.hide()
		
		fullname = self.current_user_properties.Get("(ss)",
			USER_IFACE,
			"Fullname"
		)
		self.objects.fullname.set_markup(fullname if fullname else NO_FULLNAME_STRING)
		
		self.objects.change_fullname_button.set_image(self.objects.edit_image)
		
		self.on_edit_mode = False
	
	def on_change_fullname_button_clicked(self, button):
		"""
		Fired when the 'Edit fullname' button has been clicked.
		"""
		
		if not self.on_edit_mode:
			self.objects.fullname.hide()
			self.objects.new_fullname.show()
			
			self.objects.new_fullname.set_text(
				self.objects.fullname.get_text() if self.objects.fullname.get_text() != NO_FULLNAME_STRING.replace("<i>","").replace("</i>","") else ""
			)
			self.objects.new_fullname.grab_focus()
			
			self.objects.change_fullname_button.set_image(self.objects.apply_image)
			
			self.on_edit_mode = True
		else:
			# Save changes
			self.current_user_properties.Set("(sss)",
				USER_IFACE,
				"Fullname",
				self.objects.new_fullname.get_text()
			)
			
			self.current_user_box.set_username_and_fullname(
				self.current_user_box.user.get_text(),
				self.objects.new_fullname.get_text()
			)
			
			self.restore_edit_mode()
	
	def on_change_password_button_clicked(self, button):
		"""
		Fired when the 'Click to change' button on the password field
		has been clicked.
		"""
		
		self.current_user.ChangePassword('(s)', os.environ["DISPLAY"])
	
	def on_delete_user_button_clicked(self, button):
		"""
		Fired when the delete user button has been clicked.
		"""
		
		self.objects.delete_user_dialog.show()
	
	def on_delete_user_dialog_response(self, dialog, response_id):
		"""
		Fired when the delete user dialog got a response.
		"""
		
		if response_id == Gtk.ResponseType.OK:
			# Delete user
			# FIXME: error checking?
			self.current_user.DeleteUser("(b)", self.objects.delete_user_with_home.get_active())
		
		# Reset delete_user_with_home
		self.objects.delete_user_with_home.set_active(False)
		dialog.hide()
		return False
	
	def on_change_groups_button_clicked(self, dialog):
		"""
		Fired when the change groups button has been clicked.
		"""
		
		self.objects.groups_store.clear()
		
		# Build group list
		user_in = self.GroupConfig.GetGroupsForUser('(s)', self.current_user_box._user)
		for group, name in self.GroupConfig.GetGroups().items():
			name = name[0]
			if name in ("sudo",):
				# Skip
				continue
			self.objects.groups_store.insert_with_valuesv(-1, [0, 1, 2], [group, (name in user_in), name])
		
		self.objects.groups_dialog.show()
	
	def on_groups_dialog_response(self, dialog, response_id):
		"""
		Fired when the groups dialog got a response.
		"""
		
		dialog.hide()
		return False
	
	def on_group_enabled_toggle_toggled(self, toggle, path):
		"""
		Fired when a toggle in the groups dialog has been... toggled.
		"""
		
		itr = self.objects.groups_store.get_iter(path)
		
		# Connect to group object
		group_properties = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/semplicelinux/usersd/group/%s" % self.objects.groups_store.get_value(itr, 0),
			"org.freedesktop.DBus.Properties",
			self.bus_cancellable
		)
		
		# Get current group members
		members = group_properties.Get('(ss)', 'org.semplicelinux.usersd.group', 'Members')
		
		if not toggle.get_active():
			# Add user
			if not self.current_user_box._user in members: members.append(self.current_user_box._user)
		else:
			# Remove user
			if self.current_user_box._user in members: members.remove(self.current_user_box._user)
		
		# Set the new list
		try:
			group_properties.Set('(ssas)', 'org.semplicelinux.usersd.group', 'Members', members)
		except:
			# Failed/Aborted
			return
		
		# Finally set the enabled boolean in the row
		self.objects.groups_store.set_value(itr, 1, not toggle.get_active())
			
	@quickstart.threads.on_idle
	def build_user_list(self):
		"""
		Builds the user list.
		"""
		
		# Clear
		self.objects.user_list.foreach(lambda x: x.destroy())
		
		# "Add new"
		self.objects.user_list.add(AddNewBox())
		
		try:
			for uid, details in self.UsersConfig.GetUsers().items():
				if uid < 1000 or uid == 65534:
					# Skip system groups or nobody
					continue
				
				box = Gtk.ListBoxRow()
				box.add(UserBox(uid, details[0], details[1], details[2]))
				box.show()
				self.objects.user_list.add(box)
				
				# Current user?
				if uid == CURRENT_UID:
					# Yes!
					self.caller_user_box = box
					self.objects.user_list.select_row(self.caller_user_box)
		except:
			# Unable to build user list, probably caused by a non-working DBus connection
			self.objects.main.set_sensitive(False)
			self.objects.content.hide()
			self.objects.unable_to_connect_warning.show()
			
	def on_user_list_row_selected(self, listbox, row):
		"""
		Fired when a user has been selected.
		"""
		
		if row == None: return
		
		userbox = row.get_child()
		
		if userbox.add_new:
			return self.UsersConfig.ShowUserCreationUI('(sas)', os.environ["DISPLAY"], DEFAULT_GROUPS)
		
		self.current_user_box = userbox
		
		# Caller users cannot remove themselves
		if row == self.caller_user_box:
			self.objects.delete_user_button.hide()
		else:
			self.objects.delete_user_button.show()
		
		# Obtain DBus object for the current user
		self.current_user = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/semplicelinux/usersd/user/%s" % userbox.uid,
			USER_IFACE,
			self.bus_cancellable
		)
		self.current_user_properties = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/semplicelinux/usersd/user/%s" % userbox.uid,
			"org.freedesktop.DBus.Properties",
			self.bus_cancellable
		)
		
		self.objects.fullname.set_markup(userbox.fullname.get_text() if userbox.fullname.get_text() else NO_FULLNAME_STRING)
		self.objects.user.set_text(userbox.user.get_text())
		
		# Administrator switch
		if self.SudoGroup:
			self.objects.administrator.set_active(
				(userbox.user.get_text() in self.SudoGroup.Get('(ss)', 'org.semplicelinux.usersd.group', 'Members'))
			)
	
	def determine_row_sorting(self, row1, row2):
		"""
		Used to sort the user list by UIDs.
		"""
		
		child1 = row1.get_child()
		child2 = row2.get_child()
		
		if child2.add_new:
			return 1
		elif child1.add_new:
			return 0
		elif child1.uid > child2.uid:
			return 1
		else:
			return 0
	
	def prepare_scene(self):
		"""
		Fired when the module has just been loaded and we should setup
		things.
		"""
		
		self.scene_container = self.objects.main
		
		# g-signals
		self.signal_handlers = {
			"UserListChanged": self.build_user_list
		}

		# Create unlockbar
		self.unlockbar = UnlockBar("org.semplicelinux.usersd.manage")
		self.unlockbar.connect("locked", self.on_locked)
		self.unlockbar.connect("unlocked", self.on_unlocked)
		self.objects.main.pack_start(self.unlockbar, False, False, 0)
		
		# Bind the locked state to the sensitiveness of the use_scrolled ScrolledWindow
		self.unlockbar.bind_property(
			"lock",
			self.objects.user_scrolled,
			"sensitive",
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
		)
		
		# ListBox sort
		self.objects.user_list.set_sort_func(self.determine_row_sorting)
		
		# Delete user dialog
		self.objects.delete_user_dialog.bind_property(
			"visible",
			self.objects.main,
			"sensitive",
			GObject.BindingFlags.DEFAULT | GObject.BindingFlags.INVERT_BOOLEAN
		)
		self.objects.delete_user_dialog.add_buttons(
			_("_Cancel"),
			Gtk.ResponseType.CANCEL,
			_("_Delete user"),
			Gtk.ResponseType.OK
		)
		self.objects.delete_user_dialog.get_widget_for_response(Gtk.ResponseType.OK).get_style_context().add_class("destructive-action")
		
		# Groups dialog
		self.objects.groups_dialog.bind_property(
			"visible",
			self.objects.main,
			"sensitive",
			GObject.BindingFlags.DEFAULT | GObject.BindingFlags.INVERT_BOOLEAN
		)
		self.objects.groups_dialog.add_buttons(
			_("_Close"),
			Gtk.ResponseType.CLOSE
		)

		self.group_enabled_toggle = Gtk.CellRendererToggle()
		self.objects.groups_treeview.append_column(
			Gtk.TreeViewColumn(
				"Enabled",
				self.group_enabled_toggle,
				active=1
			)
		)
		self.group_enabled_toggle.connect("toggled", self.on_group_enabled_toggle_toggled)
		self.objects.groups_treeview.append_column(
			Gtk.TreeViewColumn(
				"Group description",
				Gtk.CellRendererText(),
				text=2
			)
		)
		self.objects.groups_store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
		
		self.objects.administrator.connect("notify::active", self.on_administrator_changed)
	
	def on_administrator_changed(self, widget, param):
		"""
		Fired when the user wants to change the sudo membership of the selected user.
		"""
		
		members = self.SudoGroup.Get('(ss)', 'org.semplicelinux.usersd.group', 'Members')
		
		changed = False
		if widget.get_active():
			# Add
			if not self.current_user_box._user in members:
				members.append(self.current_user_box._user)
				changed = True
		else:
			# Remove
			if self.current_user_box._user in members:
				members.remove(self.current_user_box._user)
				changed = True
		
		if changed:
			# Commit changes
			self.SudoGroup.Set('(ssas)', 'org.semplicelinux.usersd.group', 'Members', members)		

	def on_scene_called(self):
		"""
		Fired when the user wants to see this scene.
		"""
		
		# Recover from a failed connection state
		self.objects.main.set_sensitive(True)
		self.objects.content.show()
		self.objects.unable_to_connect_warning.hide()
		
		# We are locked!
		self.unlockbar.emit("locked")
		
		# Estabilish DBus connection
		self.bus_cancellable = Gio.Cancellable()
		self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, self.bus_cancellable)
		self.UsersConfig = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/semplicelinux/usersd",
			"org.semplicelinux.usersd.user",
			self.bus_cancellable
		)
		self.UsersConfig.connect(
			"g-signal",
			lambda proxy, sender, signal, params: self.signal_handlers[signal]() if signal in self.signal_handlers else None
		)
		self.GroupConfig = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/semplicelinux/usersd",
			"org.semplicelinux.usersd.group",
			self.bus_cancellable
		)
		
		# Estabilish DBus connection to the "sudo" group
		try:
			self.SudoGroup = Gio.DBusProxy.new_sync(
				self.bus,
				0,
				None,
				BUS_NAME,
				self.GroupConfig.LookupGroup("(s)", "sudo"),
				"org.freedesktop.DBus.Properties",
				self.bus_cancellable
			)
		except:
			self.SudoGroup = None
		
		if not self.SudoGroup:
			self.objects.administrator.set_sensitive(False)
		else:
			self.objects.administrator.set_sensitive(True)
		
		self.build_user_list()			

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

from gi.repository import Gtk, Gio, GObject, Polkit

from enum import IntEnum

ActionResponse = IntEnum("ActionResponse", "UNLOCK LOCK")

# Get authority and subject
authority = Polkit.Authority.get()
subject = Polkit.UnixProcess.new(os.getpid())
#subject = Polkit.UnixSession.new_for_process_sync(os.getppid())

class UnlockBar(Gtk.InfoBar):
	
	"""
	A SectionFrame is a special GtkFrame with a IconView that houses all
	the revelant VeraCCmodules.
	"""
	
	__gsignals__ = {
		"locked" : (GObject.SIGNAL_RUN_FIRST, None, ()),
		"unlocked" : (GObject.SIGNAL_RUN_FIRST, None, ())
	}
	
	__gproperties__ = {
		"lock" : (
			GObject.TYPE_BOOLEAN,
			"Locked",
			"True if locked, False if not.",
			True,
			GObject.PARAM_READWRITE
		)
	}
	
	def do_get_property(self, property):
		"""
		Returns the value of the specified property
		"""
		
		if property.name == "lock":
			return True if self.current_state == ActionResponse.LOCK else False
		else:
			raise AttributeError("unknown property %s" % property.name)
	
	def do_set_property(self, property, value):
		"""
		You can't set properties.
		"""
		
		pass
		#raise Exception("you can't set UnlockBar properties.")
		
	
	def do_locked(self):
		"""
		Method handler for the 'locked' signal.
		"""
		
		self.current_state = ActionResponse.LOCK
		self.props.lock = True # Just to notify
		self.lock_bar()
	
	def do_unlocked(self):
		"""
		Method handler for the 'unlocked' signal.
		"""
		
		self.current_state = ActionResponse.UNLOCK
		self.props.lock = False # Just to notify
		self.unlock_bar()
	
	def __init__(self, action_id, locked_message=None, unlocked_message=None):
		"""
		Initializes the object.
		"""
		
		super().__init__()
		
		self.current_state = ActionResponse.LOCK # Default to locked
		
		# Action id
		self.action_id = action_id
		
		# Cancellable
		self.cancellable = None
		
		self.label = Gtk.Label()
		self.get_content_area().add(self.label)
		
		if not locked_message:
			self.locked_message = _("You need additional privileges to modify these settings.")
		else:
			self.locked_message = locked_message
		
		if not unlocked_message:
			self.unlocked_message = _("Press the <i>Lock</i> button to lock these settings.")
		else:
			self.unlocked_message = unlocked_message
		
		self.unlock_button = self.add_button(_("_Unlock"), ActionResponse.UNLOCK)
		self.lock_button = self.add_button(_("_Lock"), ActionResponse.LOCK)
		
		# Handle the lock/unlock button
		self.connect("response", self.on_response)
		
		self.show_all()
	
	def on_response(self, infobar, responseid):
		"""
		Fired when the user clicks the Lock/Unlock button.
		"""
		
		if responseid == ActionResponse.UNLOCK:
			# We should unlock!
			
			# Create a new cancellable
			self.cancellable = Gio.Cancellable()
			
			authority.check_authorization(
				subject,
				self.action_id,
				None,
				Polkit.CheckAuthorizationFlags.ALLOW_USER_INTERACTION,
				self.cancellable,
				self.on_authorization_response
			)
		elif responseid == ActionResponse.LOCK:
			# We should lock.
			
			self.cancel_authorization()
	
	def on_authorization_response(self, authority, res):
		"""
		Fired when the authority has decided about the authorization.
		"""
		
		try:
			result = authority.check_authorization_finish(res)
			if result.get_is_authorized():
				# Yay!!
				self.emit("unlocked")
			elif result.get_is_challenge():
				# Challenge
				print("Challenge")
			else:
				# Not authorized
				print("Not authorized")
		except GObject.GError as error:
			self.error_bar(error.message)
	
	def cancel_authorization(self):
		"""
		Fired when a timer has expired (or the application has requested
		the expiration of the authorization)
		"""
		
		if self.cancellable:
			self.cancellable.cancel()
			self.emit("locked")
					
		return False
	
	def lock_bar(self):
		"""
		Locks the bar.
		"""
		
		# Set text
		self.label.set_markup(self.locked_message)
		
		# Set message type (warning)
		self.set_message_type(Gtk.MessageType.WARNING)
		
		self.lock_button.hide()
		self.unlock_button.show()
		
	def unlock_bar(self):
		"""
		Unlocks the bar.
		"""
		
		# Set text
		self.label.set_markup(self.unlocked_message)
		
		# Set message type (info)
		self.set_message_type(Gtk.MessageType.INFO)
		
		self.lock_button.show()
		self.unlock_button.hide()

	def error_bar(self, message):
		"""
		Displays an error in the bar.
		"""
		
		# Set text
		self.label.set_markup(_("Error checking authorization: %s") % message)
		
		# Set message type (error)
		self.set_message_type(Gtk.MessageType.ERROR)
		
		self.lock_button.hide()
		self.unlock_button.show()
		
		

# -*- coding: utf-8 -*-
#
# vera-control-center - Vera Control Center
# Copyright (C) 2014-2015  Semplice Project
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

from gi.repository import Gtk, Gio, GObject

from veracc.utils import Settings

class RebootDialog(Gtk.MessageDialog):
	"""
	A RebootDialog() is a dialog that displays a "Reboot now" request
	to the user.
	"""
	
	REBOOT_NOW_STRING = _("_Reboot now (in %ds)")
	
	def on_dialog_response(self, dialog, response):
		"""
		Fired when the dialog generated a response.
		"""
		
		# Reset the countdown
		self.countdown = self.settings.get_int("exit-window-countdown")
		
		# Stop the timeout
		if self.timeout_id > -1:
			GObject.source_remove(self.timeout_id)
		
		if response == Gtk.ResponseType.OK:
			self.Vera.Reboot()
		
		self.hide()
	
	def process_countdown(self):
		"""
		Processes the countdown.
		"""
				
		self.countdown -= 1
		
		if self.countdown == 0:
			# Assume we're OK
			self.emit("response", Gtk.ResponseType.OK)
			
			return False
		else:
			self.get_widget_for_response(Gtk.ResponseType.OK).set_label(self.REBOOT_NOW_STRING % self.countdown)
			
			return True
	
	def on_dialog_shown(self, dialog):
		"""
		Fired when the dialog has been shown.
		"""
		
		# Start the timeout
		if self.countdown > 0:
			self.timeout_id = GObject.timeout_add_seconds(1, self.process_countdown)
	
	def __init__(self, cancellable):
		"""
		Initializes the class.
		"""
		
		super().__init__()
		
		self.settings = Settings("org.semplicelinux.vera")
		
		self.timeout_id = -1
		
		self.countdown = self.settings.get_int("exit-window-countdown")
		
		# The dialog may be unexpected, so if the countdown setting is < 10,
		# default to 10 to be on the safe side
		if self.countdown > 0 and self.countdown < 10:
			self.countdown = 10
		
		self.cancellable = cancellable

		self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, self.cancellable)
		self.Vera = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			"org.semplicelinux.vera",
			"/org/semplicelinux/vera",
			"org.semplicelinux.vera",
			self.cancellable
		)
		
		self.set_title(_("Reboot"))
		self.set_modal(True)
		
		self.set_markup("<big>%s</big>" % _("Reboot required"))
		self.format_secondary_text(
			_(
"""In order to apply the changes, a reboot is required.

Please save your work and press "Reboot now" to reboot or press "Cancel" to reboot later."""
			)
		)
		
		self.add_buttons(
			_("_Cancel"),
			Gtk.ResponseType.CANCEL,
			
			self.REBOOT_NOW_STRING % self.countdown
			if self.countdown > 0 else
			_("_Reboot now"),
			Gtk.ResponseType.OK
		)
		
		self.set_default_response(Gtk.ResponseType.OK)
		
		self.connect("show", self.on_dialog_shown)
		self.connect("response", self.on_dialog_response)

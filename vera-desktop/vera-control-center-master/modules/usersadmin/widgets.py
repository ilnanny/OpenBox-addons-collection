# -*- coding: utf-8 -*-
#
# usersadmin - Manage users and groups
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

from gi.repository import Gtk

class AddNewBox(Gtk.Box):
	"""
	An AddNewBox is a box with the "Add new user" label.
	"""
	
	add_new = True
	
	def __init__(self):
		"""
		Initializes the box.
		"""
		
		super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
		
		self.icon = Gtk.Image.new_from_icon_name("gtk-add", Gtk.IconSize.DIALOG)
		self.label = Gtk.Label(_("Add a new user"))
		
		self.pack_start(self.icon, False, False, 0)
		self.pack_start(self.label, False, False, 2)
		
		self.show_all()
		

class UserBox(Gtk.Box):
	"""
	An UserBox contains the avatar, Full name and username of the user.
	"""
	
	add_new = False
	
	def __init__(self, uid, user, fullname, home):
		"""
		Initializes the box.
		"""
		
		super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
		
		self.uid = uid
		
		self.avatar = Gtk.Image.new_from_icon_name("avatar-default", Gtk.IconSize.DIALOG)
		self.inner_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.fullname = Gtk.Label()
		self.fullname.set_alignment(0, 0.5)
		self.user = Gtk.Label()
		self.user.set_alignment(0, 0.5)
		
		self.inner_container.pack_start(self.fullname, True, True, 0)
		self.inner_container.pack_start(self.user, True, True, 2)
		
		self.pack_start(self.avatar, False, False, 0)
		self.pack_start(self.inner_container, False, False, 2)
		
		self.show_all()
		
		self.set_username_and_fullname(user, fullname)
		
		self._user = user
		self._fullname = fullname
	
	def set_username_and_fullname(self, user, fullname):
		"""
		Sets the username and fullname in the box.
		"""

		if not fullname:
			self.user.set_markup("<b>%s</b>" % user)
			self.fullname.hide()
		else:
			self.fullname.set_markup("<b>%s</b>" % fullname)
			self.user.set_text(user)
			self.fullname.show()

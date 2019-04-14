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

from gi.repository import Gtk

import quickstart.threads

class CommonFrame(Gtk.Frame):
	
	"""
	A GtkFrame commonly used by veracc's modules.
	"""
	
	def __init__(self, name):
		"""
		Initializes the object.
		"""
		
		super().__init__()
		
		# Set the label and link it to the frame
		self.label = Gtk.Label()
		self.label.set_markup("<b>%s</b>" % name)
		self.set_label_widget(self.label)
		
		self.set_shadow_type(Gtk.ShadowType.NONE)
		
		# Some styling
		self.set_shadow_type(Gtk.ShadowType.NONE)
		
		# Add an alignment
		self._alignment = Gtk.Alignment()
		self._alignment.set_padding(2, 2, 12, 0)
		
		self.add(self._alignment)
	
	def get_alignment(self):
		"""
		Convenience method to get the child alignment.
		"""
		
		return self._alignment

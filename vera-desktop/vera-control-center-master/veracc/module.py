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

from xdg.DesktopEntry import DesktopEntry

from gi.repository import Gtk

ICON_THEME = Gtk.IconTheme.get_default()

class VeraCCModule:
	""" An object representing a Vera Control Center module. """
		
	def __init__(self, module_name, module_path):
		""" Initialize the object """
				
		self.module_is_external = False
		self.module_name = module_name
		self.module_path = module_path
	
		self.launcher_icon = None
		self.launcher_name = None
		self.launcher_comment = None
		self.launcher_section = None
			
		self.module_launcher = DesktopEntry(os.path.join(self.module_path, "%s.desktop" % self.module_name))
			
		# Icon
		self.launcher_icon = self.module_launcher.getIcon()
		if not self.launcher_icon:
			self.launcher_icon = "preferences-system"

		#ICON_THEME.connect("changed", lambda x: self.replace_icon(icon))
		
		# Name
		self.launcher_name = self.module_launcher.getName()
		
		# Comment
		self.launcher_comment = self.module_launcher.getComment()
		
		# Section
		self.launcher_section = self.module_launcher.get("X-VeraCC-Section")
		
		# Keywords
		self.launcher_keywords = [x.lower() for x in self.module_launcher.getKeywords()]
		
		# External?
		_exec = self.module_launcher.getExec()
		if _exec:
			# Yeah!
			self.module_is_external = True
			self.module_path = _exec
		
		

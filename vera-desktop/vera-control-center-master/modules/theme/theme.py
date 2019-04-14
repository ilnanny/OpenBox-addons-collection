# -*- coding: utf-8 -*-
#
# theme - Appearance module for Vera Control Center
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

from gi.repository import Gtk, Gio
import quickstart

from veracc.utils import Settings

from .pages.gtktheme import GtkTheme
from .pages.paranoid import Paranoid
from .pages.font import Fonts

class Scene(quickstart.scenes.BaseScene):
	""" Theme preferences. """
	
	def prepare_scene(self):
		""" Called when doing the scene setup. """
		
		# Settings
		self.settings = Settings("org.semplicelinux.vera.settings")
		self.openboxsettings = Settings("org.semplicelinux.vera.openbox")
		
		self.scene_container = Gtk.Alignment()
		self.scene_container.set_padding(10, 10, 10, 10)
		
		self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		
		self.stack = Gtk.Stack()
		self.stack.set_homogeneous(False)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		self.stack_switcher = Gtk.StackSwitcher()
		self.stack_switcher.set_halign(Gtk.Align.CENTER)
		self.stack_switcher.set_stack(self.stack)
		
		self.container.pack_start(self.stack_switcher, False, False, 0)
		self.container.pack_start(self.stack, True, True, 0)
		
		# Gtk theme page
		self.stack.add_titled(GtkTheme(self.settings, self.openboxsettings), "gtktheme", _("Theme"))
		self.stack.add_titled(Paranoid(self.settings), "paranoid", _("Effects"))
		self.stack.add_titled(Fonts(self.settings, self.openboxsettings), "font", _("Fonts"))
		
		self.scene_container.add(self.container)
		self.scene_container.show_all()

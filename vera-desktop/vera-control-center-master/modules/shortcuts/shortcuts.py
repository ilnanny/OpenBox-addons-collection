# -*- coding: utf-8 -*-
#
# shortcuts - shortcuts module for Vera Control Center
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

import quickstart

from gi.repository import Gtk

from veracc.utils import Settings

# A bit hacky, but it seems we can't set directly the enum value in GSettings :(
ALLOWED_ACTIONS = [
	'PowerOff',
	'Reboot',
	'Suspend',
	'Logout',
	'Lock',
	'Hibernate',
	'Switch User'
]

@quickstart.builder.from_file("./modules/shortcuts/shortcuts.glade")
class Scene(quickstart.scenes.BaseScene):
	"""
	Shortcuts preferences.
	"""
	
	events = {
		"toggled" : ("enable_launcher",)
	}
	
	def convert_exit_action_from_dconf(self, value):
		"""
		Converts the exit action from dconf.
		"""
		
		value = self.settings.get_enum("last-exit-action")
		
		if not self.settings.get_boolean("lock-last-exit-action"):
			# Not locked, this is the "Last action" item
			return 0
		else:
			return value
	
	def convert_exit_action_from_ui(self, value):
		"""
		Converts the exit action from the UI.
		"""
				
		if value == 0:
			# Not locked, unset lock-last-exit-action
			self.settings.set_boolean("lock-last-exit-action", False)
			return self.settings.get_string("last-exit-action")
		else:
			self.settings.set_boolean("lock-last-exit-action", True)
			return ALLOWED_ACTIONS[value-1]
	
	def on_enable_launcher_toggled(self, checkbutton):
		"""
		Fired when the "Enable launcher" checkbutton has been toggled.
		"""
		
		self.objects.enable_launcher_notice.set_visible(
			not self.objects.enable_launcher_notice.get_visible()
		)
	
	def prepare_scene(self):
		"""
		Scene set-up.
		"""
		
		self.scene_container = self.objects.main
		
		self.settings = Settings("org.semplicelinux.vera")
		self.desktop_settings = Settings("org.semplicelinux.vera.desktop")
		
		# Set-up actions combobox
		renderer = Gtk.CellRendererText()
		self.objects.last_exit_action.pack_start(renderer, True)
		self.objects.last_exit_action.add_attribute(renderer, "text", 0)
		self.settings.bind_with_convert(
			"last-exit-action",
			self.objects.last_exit_action,
			"active",
			self.convert_exit_action_from_dconf,
			self.convert_exit_action_from_ui
		)
		
		# Confirmation window
		self.settings.bind(
			"hide-exit-window",
			self.objects.hide_exit_window,
			"active"
		)
		
		# Ninja shortcut
		self.settings.bind(
			"ninja-shortcut",
			self.objects.ninja_shortcut,
			"active"
		)
		
		# Ninja container
		self.objects.ninja_shortcut.bind_property(
			"active",
			self.objects.ninja_container,
			"sensitive"
		)
		
		# Desktop launcher
		self.desktop_settings.bind(
			"show-launcher",
			self.objects.enable_launcher,
			"active"
		)

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

from gi.repository import Gio, GLib

class Settings(Gio.Settings):
	"""
	Nicey things.
	"""
	
	def __init__(self, schema_id):
		"""
		Initializes the class.
		"""

		super().__init__(schema_id)
		
		# Needed for bind_with_convert
		self._ignore_key_changed = False
		self._ignore_prop_changed = True
	
	def bind(self, key, obj, prop, flags=Gio.SettingsBindFlags.DEFAULT):
		"""
		A simplified version of bind().
		"""
		
		return Gio.Settings.bind(self, key, obj, prop, flags)
	
	def bind_with_convert(self, key, widget, prop, key_to_prop, prop_to_key):
		"""
		Recreate g_settings_bind_with_mapping from scratch.
		
		This method was shamelessly stolen from Robert Park's
		gottengeography who shamelessly stolen it from John Stowers'
		gnome-tweak-tool on May 14, 2012.
		
		:) Thank you guys!
		"""
		
		def key_changed(settings, key):
			"""Update widget property."""
			
			if self._ignore_key_changed:
				return
			
			self._ignore_prop_changed = True
			
			widget.set_property(prop, key_to_prop(self[key]))
			
			self._ignore_prop_changed = False

		def prop_changed(widget, param):
			"""Update GSettings key."""
			
			if self._ignore_prop_changed:
				return
			
			self._ignore_key_changed = True
			
			try:
				self[key] = prop_to_key(widget.get_property(prop))
			except NotImplementedError:
				#
				# Force storage of ranges, without checking.
				# Unfortunately if the key value != type or enum,
				# Gio.Settings' __setitem__ will raise NotImplementedError.
				# As our input is usually checked, we can safely force
				# the storage of the property.
				#
				range_ = self.get_range(key)
				type_ = range_.get_child_value(0).get_string()
				if type_ == "range":
					self.set_value(key, GLib.Variant('i', widget.get_property(prop)))
			
			self._ignore_key_changed = False

		self.connect('changed::' + key, key_changed)
		widget.connect('notify::' + prop, prop_changed)
		key_changed(self, key) # init default state

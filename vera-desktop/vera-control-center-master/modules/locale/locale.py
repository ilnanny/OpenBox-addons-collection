# -*- coding: utf-8 -*-
#
# locale - locale module for Vera Control Center
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
import quickstart

from veracc.widgets.UnlockBar import UnlockBar, ActionResponse
from veracc.widgets.RebootDialog import RebootDialog

from keeptalking2.Locale import Locale

from gi.repository import Gtk, Gio, GObject

@quickstart.builder.from_file("./modules/locale/locale.glade")
class Scene(quickstart.scenes.BaseScene):
	""" Desktop preferences. """
	
	events = {
		"toggled": ("show_all", "savespace_enable"),
		"cursor-changed": ("locale_view",),
	}
	
	@quickstart.threads.thread
	def set_locale(self, locale, sel, itr):
		"""
		Sets the given locale.
		"""
		
		try:
			self.Locale.set(locale)
			self.default = itr
			
			# Create stamp
			self.Locale.create_stamp([".alan2-locale-changed"])
			
			GObject.idle_add(self.RebootDialog.show)
		except:
			sel.select_iter(self.default)

		GObject.idle_add(self.objects.region_spinner.hide)
		GObject.idle_add(self.scene_container.set_sensitive, True)
	
	@quickstart.threads.thread
	def savespace_purge(self, locale):
		"""
		Purges foreign locales.
		"""
		
		self.Locale.savespace_purge(locale)
		
		GObject.idle_add(self.objects.other_spinner.hide)
		GObject.idle_add(self.scene_container.set_sensitive, True)
	
	def on_locale_view_cursor_changed(self, locale_view):
		"""
		Fired when the user changes the locale.
		"""
				
		# selection
		sel = self.objects.locale_view.get_selection()
		if not sel: return
		
		# iter
		model, itr = sel.get_selected()
		if not itr: return
		
		selected = self.objects.locales.get_value(itr, 0)
		if selected == self.Locale.default: return
		
		if self.objects.savespace_enable.get_active():
			# Display warning
			if self.objects.savespace_warning.run() == Gtk.ResponseType.NO:
				self.objects.savespace_warning.hide()
				
				sel.select_iter(self.default)
				return
			
			self.objects.savespace_enable.set_active(False)
			self.objects.savespace_warning.hide()
		
		GObject.idle_add(self.objects.region_spinner.show)
		GObject.idle_add(self.scene_container.set_sensitive, False)
		
		self.set_locale(selected, sel, itr)
	
	def on_show_all_toggled(self, checkbutton):
		"""
		Fired when the 'Show all locales' checkbutton has been clicked.
		"""
		
		GObject.idle_add(self.build_locale_list, self.objects.show_all.get_active())
	
	def on_savespace_enable_toggled(self, checkbutton):
		"""
		Fired when the 'Enable savespace' checkbutton has been clicked.
		"""
		
		locale = self.objects.locales.get_value(self.default, 0)
		
		if checkbutton.get_active():
			self.Locale.savespace_enable(locale)
			
			# Purge window
			if self.objects.savespace_window.run() == Gtk.ResponseType.YES:
				# Purge!!
				self.savespace_purge(locale)
				
				GObject.idle_add(self.objects.other_spinner.show)
				GObject.idle_add(self.scene_container.set_sensitive, False)
			self.objects.savespace_window.hide()
		else:
			self.Locale.savespace_disable()
	
	def build_locale_list(self, all=False):
		"""
		Populates the listbox with locales.
		"""
		
		self.objects.locales.clear()
				
		for locale, human in self.Locale.human_form(all=all).items():
			if all:
				codepage = self.Locale.codepages[locale]
			else:
				codepage = ""
			itr = self.objects.locales.append((locale, human, codepage))
			
			# Save iter if this is the default...
			if locale == self.Locale.default:
				self.default = itr
		
		if self.default:
			sel = self.objects.locale_view.get_selection()
			sel.select_iter(self.default)
						
			GObject.idle_add(self.objects.locale_view.scroll_to_cell, sel.get_selected_rows()[1][0])
	
	def on_locked(self, unlockbar):
		"""
		Fired when the scene has been locked.
		"""
		
		GObject.idle_add(self.objects.content.set_sensitive, False)
	
	def on_unlocked(self, unlockbar):
		"""
		Fired when the scene has been unlocked.
		"""
		
		GObject.idle_add(self.objects.content.set_sensitive, True)
	
	def prepare_scene(self):
		""" Called when doing the scene setup. """
		
		self.scene_container = self.objects.main
		
		# Check for savespace...
		if os.path.exists("/etc/dpkg/dpkg.cfg.d/keeptalking"):
			self.objects.savespace_enable.set_active(True)
		
		# Create unlockbar
		self.unlockbar = UnlockBar("org.semplicelinux.keeptalking2.change-locale")
		self.unlockbar.connect("locked", self.on_locked)
		self.unlockbar.connect("unlocked", self.on_unlocked)
		self.objects.main.pack_start(self.unlockbar, False, False, 0)		

		self.Locale = Locale()
		
		self.default = None

		# Make the locale_view treeview working...
		locale_renderer = Gtk.CellRendererText()
		self.locale_column = Gtk.TreeViewColumn("Locale", locale_renderer, text=1)
		self.objects.locales.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		self.objects.locale_view.append_column(self.locale_column)
		
		type_renderer = Gtk.CellRendererText()
		self.type_column = Gtk.TreeViewColumn("Type", type_renderer, text=2)
		self.objects.locale_view.append_column(self.type_column)

		# Populate the locale list
		GObject.idle_add(self.build_locale_list)
	
	def on_scene_called(self):
		"""
		Show the scene!
		"""
		
		# We are locked
		self.unlockbar.emit("locked")
		
		self.cancellable = Gio.Cancellable()
		self.RebootDialog = RebootDialog(self.cancellable)
		self.RebootDialog.bind_property(
			"visible",
			self.scene_container,
			"sensitive",
			GObject.BindingFlags.INVERT_BOOLEAN
		)

	def on_scene_asked_to_close(self):
		"""
		Do some cleanup before returning home
		"""
		
		self.unlockbar.cancel_authorization()
		self.cancellable.cancel()
		
		return True

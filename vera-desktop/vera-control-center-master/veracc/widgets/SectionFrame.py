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
from gi.repository.GdkPixbuf import Pixbuf

import quickstart.threads

from veracc.widgets.CommonFrame import CommonFrame

ICON_THEME = Gtk.IconTheme.get_default()

class SectionFrame(CommonFrame):
	
	"""
	A SectionFrame is a special GtkFrame with a IconView that houses all
	the revelant VeraCCmodules.
	"""
	
	FILTER = ""
	
	def obtain_icon(self, icon):
		"""
		Returns a Pixbuf with the loaded icon.
		"""
		
		if not ICON_THEME.has_icon(icon):
			icon = "preferences-system"
		
		return ICON_THEME.load_icon(icon, 48, 0)
	
	def reload_all_icons(self):
		"""
		Reloads all icons in the liststore.
		It's used when the Icon Theme has been changed.
		"""
		
		# FIXME: Is there a cleaner, more pythonic way to loop through
		# iters? If yes, we should probably change this method.
		
		iter_ = self.liststore.get_iter_first()
		
		while iter_:
			self.liststore[iter_][0] = self.obtain_icon(self.liststore[iter_][6])
			
			iter_ = self.liststore.iter_next(iter_)
	
	def search(self, keyword):
		"""
		Sets self.FILTER to keyword and then triggers a refilter.
		"""
		
		self.FILTER = keyword
		self.filter.refilter()
	
	def on_refilter(self, model, iter_, data):
		"""
		Returns True if the iter should be visible given the current
		keyword, False if not.
		"""
		
		name = self.liststore[iter_][1].lower()
		keywords = self.liststore[iter_][7]
		
		if not self.FILTER or name.startswith(self.FILTER):
			return True
		else:
			# Our last try is with the keywords
			for key in keywords:
				if key.startswith(self.FILTER):
					return True
			
			return False
	
	def __init__(self, name):
		"""
		Initializes the object.
		"""
		
		super().__init__(name)
				
		self.label = Gtk.Label()
		self.liststore = Gtk.ListStore(Pixbuf, str, str, str, str, bool, str, object)
		self.liststore.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		
		# Whaaaat? filter_new() to instantiate the object?
		# This is documented *NOWHERE*!!
		self.filter = Gtk.TreeModelFilter.filter_new(self.liststore, None)
		self.filter.set_visible_func(self.on_refilter)
		
		self.iconview = Gtk.IconView()
		
		"""
		# Set the label and link it to the frame
		self.label.set_markup("<b>%s</b>" % name)
		self.set_label_widget(self.label)
		
		# Some styling
		self.set_shadow_type(Gtk.ShadowType.NONE)
		"""
		
		# Setup the iconview
		self.get_alignment().add(self.iconview)
		self.iconview.set_activate_on_single_click(True)
		self.iconview.set_columns(5)
		self.iconview.set_item_width(75)
		self.iconview.set_spacing(5)
		self.iconview.set_margin(2)
		self.iconview.set_model(self.filter)
		self.iconview.set_pixbuf_column(0)
		self.iconview.set_text_column(1)
		self.iconview.set_tooltip_column(2)
		
		# Style
		self.iconview.get_style_context().add_class("veracc-section")
		
		# Listen for eventual theme changes
		ICON_THEME.connect("changed", lambda x: self.reload_all_icons())
		
		self.show_all()
	
	@quickstart.threads.on_idle
	def populate(self, lst):
		"""
		Populates the IconView with every VeraCCModule specified in lst.
		"""
				
		for module in lst:
			self.liststore.append(
				(
					self.obtain_icon(module.launcher_icon),
					module.launcher_name,
					module.launcher_comment,
					module.module_name,
					module.module_path,
					module.module_is_external,
					module.launcher_icon,
					module.launcher_keywords
				)
			)

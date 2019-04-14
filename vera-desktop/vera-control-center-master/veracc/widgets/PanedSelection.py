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

from gi.repository import Gtk

import quickstart.threads

class SelectionView(Gtk.ScrolledWindow):
	"""
	A dumbed-down version of the Gtk.TreeView.
	"""
	
	def __init__(self):
		"""
		Initialize the SelectionView.
		"""

		# Initialize parent
		super().__init__()		

		# Create model
		self.model = Gtk.ListStore(str)
		
		# Create TreeView
		self.treeview = Gtk.TreeView(self.model)
		self.selection = self.treeview.get_selection()
		self.selection.set_mode(Gtk.SelectionMode.SINGLE)
		self.treeview.set_headers_visible(False)
		self.add(self.treeview)
		
		# Create column
		self.column = Gtk.TreeViewColumn("Selection")
		self.treeview.append_column(self.column)
		
		# Create cell renderer
		self.cellrenderer = Gtk.CellRendererText()
		self.column.pack_start(self.cellrenderer, True)
		self.column.add_attribute(self.cellrenderer, "text", 0)
	
	def append(self, name):
		"""
		Appends name to the TreeView.
		"""
		
		self.model.append((name,))
	
	def get_current_item(self):
		"""
		Gets the current item without many bad words on the developer's
		side.
		"""
		
		model, iter_ = self.selection.get_selected()
		return model.get_value(iter_, 0)

class DetailsBox(Gtk.Box):
	"""
	A Gtk.Box that provides details.
	(duh!)
	"""
	
	def __init__(self):
		"""
		Initializes the object.
		"""
		
		# Intialize parent
		super().__init__(orientation=Gtk.Orientation.VERTICAL)
		
		# Center things
		self.set_halign(Gtk.Align.CENTER)
		self.set_valign(Gtk.Align.CENTER)
		
		# Title
		self.title = Gtk.Label()
		self.title.set_line_wrap(True)
		
		self.pack_start(self.title, True, True, 0)
		
	def set_title(self, title):
		""" Sets the title. """
		
		self.title.set_markup("<big><b>%s</b></big>" % title)

class PanedSelection(Gtk.Box):
	"""
	A PanedSelection is a ready-to-use widget that makes developing
	of configuration interfaces easier.
	
	It's basically a GtkPaned with a TreeView and a DetailsBox.
	"""
	
	def get_treeview(self):
		"""
		I find ugly getting the treeview by digging into the objects,
		so this method will do that for me.
		"""
		
		return self.selection_view.treeview
	
	def __init__(self):
		"""
		Initialize the object.
		"""
		
		super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
		
		self.selection_view = SelectionView()
		self.details_box = DetailsBox()
		
		self.pack_start(self.selection_view, False, False, 0)
		self.pack_start(self.details_box, True, True, 0)
		
		self.show_all()

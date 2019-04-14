# -*- coding: utf-8 -*-
#
# about - Device information module for Vera Control Center
# Copyright (C) 2014-2016  Semplice Project
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

# 18 10

from gi.repository import Gio, Pango

import subprocess

import re
import os

import quickstart
import platform

from .osrelease import OsRelease

BUS_NAME = "org.freedesktop.hostname1"

@quickstart.builder.from_file("./modules/about/about.glade")
class Scene(quickstart.scenes.BaseScene):
	""" Desktop preferences. """
	
	events = {
		"clicked" : ("change_hostname",),
	}
	
	def on_scene_asked_to_close(self):
		"""
		Do some cleanup
		"""
		
		self.bus_cancellable.cancel()
		self.restore_edit_mode()
		
		return True
	
	def on_change_hostname_clicked(self, button):
		"""
		Fired when the 'change hostname' button has been clicked.
		"""
		
		if not self.on_edit_mode:
			self.objects.hostname.hide()
			self.objects.new_hostname.show()
			
			self.objects.new_hostname.set_text(self.get_hostname())
			self.objects.new_hostname.grab_focus()
			
			button.set_image(self.objects.apply_hostname_image)
			
			self.on_edit_mode = True
		else:
			# Save changes
			self.set_hostname(self.objects.new_hostname.get_text())
			
			self.restore_edit_mode()
	
	@quickstart.threads.on_idle
	def restore_edit_mode(self):
		"""
		Restores the edit mode.
		"""
		
		self.objects.hostname.show()
		self.objects.new_hostname.hide()
		
		self.objects.hostname.set_text(self.get_hostname())
		
		self.objects.change_hostname.set_image(self.objects.edit_hostname_image)
		
		self.on_edit_mode = False
	
	@quickstart.threads.on_idle
	def update_mem_info(self):
		"""
		Updates the memory informations.
		"""
		
		with open("/proc/meminfo", "r") as f:
			memtotal = float(f.readline().strip().split(" ")[-2]) / 1024 # MiB
			if memtotal >= 1024:
				memtotal /= 1024
				unit = "GiB"
			else:
				unit = "MiB"
		
		self.objects.memory.set_text("%.2f %s" % (memtotal, unit))
		
	@quickstart.threads.on_idle
	def update_cpu_info(self):
		"""
		Updates the cpu informations.
		"""
		
		model_name = ""
		processor_count = 0
		
		with open("/proc/cpuinfo", "r") as f:
			for line in f:
				line = line.split("\t")
				if line[0] == "processor":
					processor_count += 1
				elif not model_name and line[0] == "model name":
					model_name = line[-1].replace("\n","").replace(": ","")
		
		self.objects.cpu.set_text(
			"%s x %d" % (model_name, processor_count)
			if processor_count > 1 else model_name
		)
	
	def get_hostname(self):
		"""
		Returns the current hostname, by looking first at its Pretty version,
		and then at the internet one.
		"""
		
		hostname = self.HostnameProperties.Get('(ss)', BUS_NAME, 'PrettyHostname')
		if not hostname:
			hostname = self.HostnameProperties.Get('(ss)', BUS_NAME, 'StaticHostname')
		
		return hostname
	
	def set_hostname(self, hostname):
		"""
		Sets the given hostname.
		"""
		
		self.Hostname.SetPrettyHostname('(sb)', hostname, True)
		
		# De-pretty-ize the hostname
		ugly_hostname = hostname.lower().replace(".","-").replace(",","-").replace(
			" ","-").replace("--","-").replace("'","")
		
		ugly_hostname = re.sub("[^0-9a-z-]", '', ugly_hostname)
		
		if not ugly_hostname: ugly_hostname = "localhost"
		
		self.Hostname.SetHostname('(sb)', ugly_hostname, True)
		self.Hostname.SetStaticHostname('(sb)', ugly_hostname, True)
	
	@quickstart.threads.on_idle
	def update(self):
		"""
		Updates the page.
		"""
		
		self.objects.distro.set_text(
			"%s %s" % (self.osrelease.NAME, self.osrelease.VERSION)
		)
		self.objects.codename.set_text(self.osrelease.SEMPLICE_CODENAME)
		if self.osrelease.VERSION_ID:
			self.objects.version.set_text(self.osrelease.VERSION_ID)
		
		self.objects.hostname.set_text(self.get_hostname())
		self.update_mem_info()
		self.update_cpu_info()
		self.objects.machine.set_text(platform.machine())
	
	def prepare_scene(self):
		""" Called when doing the scene setup. """
		
		self.on_edit_mode = False
		
		self.scene_container = self.objects.main

		# Set appropriate font size and weight
		context = self.objects.distro.create_pango_context()
		desc = context.get_font_description()
		desc.set_weight(Pango.Weight.LIGHT) # Weight
		desc.set_size(Pango.SCALE*18) # Size
		self.objects.distro.override_font(desc)
		
		desc.set_size(Pango.SCALE*10)
		self.objects.codename.override_font(desc)

	def on_scene_called(self):
		"""
		Fired when the scene has been called.
		"""

		# Create the OsRelease object
		self.osrelease = OsRelease()

		# Enter in the bus
		self.bus_cancellable = Gio.Cancellable()
		self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, self.bus_cancellable)
		self.Hostname = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/hostname1",
			BUS_NAME,
			self.bus_cancellable
		)
		self.HostnameProperties = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/hostname1",
			"org.freedesktop.DBus.Properties",
			self.bus_cancellable
		) # Really we should create a new proxy to get the properties?!
		
		#self.refresh_infos()
				
		self.update()

# -*- coding: utf-8 -*-
#
# power - vera-power-manager module for Vera Control Center
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

import os

from veracc.widgets.UnlockBar import UnlockBar

from gi.repository import Gtk, Gio, GObject
from gi.repository import UPowerGlib as Up

BATTERY_STATE = {
	Up.DeviceState.UNKNOWN : _("Unknown"),
	Up.DeviceState.CHARGING : _("Charging"),
	Up.DeviceState.DISCHARGING : _("Discharging"),
	Up.DeviceState.EMPTY : _("Empty"),
	Up.DeviceState.FULLY_CHARGED : _("Fully charged"),
	Up.DeviceState.PENDING_CHARGE : _("Pending charge"),
	Up.DeviceState.PENDING_DISCHARGE : _("Pending discharge"),
	Up.DeviceState.LAST : _("Last")
}

BUS_NAME = "org.semplicelinux.vera.powermanager"

ACTIONS = ["ignore", "poweroff", "reboot", "suspend", "hibernate", "lock"]

@quickstart.builder.from_file("./modules/power/power.glade")
class Scene(quickstart.scenes.BaseScene):
	""" Desktop preferences. """
	
	events = {
		"value-changed" : ["brightness_scale"],
	}
	
	building = False
	
	client = Up.Client.new()
	with_battery = False
	
	@quickstart.threads.thread
	def set_value(self, obj, value):
		"""
		Sets the value
		"""
		
		obj('(sb)', value, True)
	
	def on_brightness_scale_value_changed(self, scale):
		"""
		Fired when the brightness level has been changed.
		"""
		
		if not self.building:
			self.VeraPowerManager.SetBrightness('(i)', int(scale.get_value())+1)
	
	def on_brightness_level_changed_external(self, params=None):
		"""
		Fired when the brightness level has been changed from the outside.
		"""
		
		if not params: params = (self.VeraPowerManager.GetBrightness(),)
		
		self.building = True
		self.objects.brightness_level.set_value(float(params[0]))
		self.building = False
	
	def on_combobox_changed(self, combobox):
		"""
		Fired when a combobox has been changed.
		"""
		
		if self.building: return
		
		if combobox == self.objects.lid_switch_action:
			# Lid switch
			obj = self.VeraPowerManager.SetHandleLidSwitch
		elif combobox == self.objects.power_button_action:
			# Power button
			obj = self.VeraPowerManager.SetHandlePowerKey
		
		self.set_value(obj, ACTIONS[combobox.get_active()])
	
	def prepare_scene(self):
		""" Called when doing the scene setup. """
		
		self.scene_container = self.objects.main
		
		# g-signals
		self.signal_handlers = {
			"BrightnessChanged" : self.on_brightness_level_changed_external,
		}
		
		# Create unlockbar
		self.unlockbar = UnlockBar("org.semplicelinux.vera.powermanager.modify-logind")
		self.objects.main.pack_start(self.unlockbar, False, False, 0)
				
		# Search for batteries
		for device in self.client.get_devices():
			if device.props.is_present and device.props.power_supply and device.props.kind == Up.DeviceKind.BATTERY:
				# Found a power supply, and we'll show this in the UI.
				self.with_battery = device
				
				# We show only one battery, otherwise the UI will be a mess
				break
		
		# If there is a battery, bind properties to get live updates on the status
		if self.with_battery:
			# Show the battery frame
			self.objects.battery_frame.show()
			
			# Name
			self.objects.battery_name.set_text(
				"%s %s" % (
					self.with_battery.props.vendor, self.with_battery.props.model
				)
			)
			
			# Percentage on charge_bar
			self.with_battery.bind_property(
				"percentage",
				self.objects.charge_bar,
				"value",
				GObject.BindingFlags.DEFAULT | GObject.BindingFlags.SYNC_CREATE
			)
			
			# Percentage on label
			# Currently python-gi doesn't support bind_property_full(), which is
			# a shame because it's fantastic.
			# So we are using a connection here.
			percentage_callback = lambda x, y: self.objects.battery_percentage.set_text("%s%%" % int(self.with_battery.props.percentage))
			self.with_battery.connect(
				"notify::percentage",
				percentage_callback
			)
			percentage_callback(None, None)
			
			# Status on label
			# Unforunately, same as above.
			status_callback = lambda x, y: self.objects.battery_status.set_text("%s, " % BATTERY_STATE[self.with_battery.props.state])
			self.with_battery.connect(
				"notify::state",
				status_callback
			)
			status_callback(None, None)
		
		# Check for lid switch
		if os.path.exists("/proc/acpi/button/lid"):
			# That's a pretty dirty check
			self.objects.lid_switch_container.show()
		
		# Create cells for the comboboxes
		for combo in (self.objects.power_button_action, self.objects.lid_switch_action):
			cellrenderer = Gtk.CellRendererText()
			combo.pack_start(cellrenderer, True)
			combo.add_attribute(cellrenderer, "text", 1)
			
			combo.connect("changed", self.on_combobox_changed)
		
		# Disable "Buttons" frame when locked
		self.unlockbar.bind_property(
			"lock",
			self.objects.buttons_frame,
			"sensitive",
			GObject.BindingFlags.DEFAULT | GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
		)
	
	def on_scene_called(self):
		"""
		Fired when the scene has been called.
		"""
		
		# Locked
		self.unlockbar.emit("locked")

		# Enter in the bus
		self.bus_cancellable = Gio.Cancellable()
		self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, self.bus_cancellable)
		self.VeraPowerManager = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/semplicelinux/vera/powermanager",
			BUS_NAME,
			self.bus_cancellable
		)
		# connect signals
		self.VeraPowerManager.connect(
			"g-signal",
			lambda proxy, sender, signal, params: self.signal_handlers[signal](params) if signal in self.signal_handlers else None
		)
		
		# Check for backlight support
		if self.VeraPowerManager.IsBacklightSupported():
			self.objects.display_frame.show()
			self.on_brightness_level_changed_external()
		else:
			self.objects.display_frame.hide()
		
		# Update comboboxes
		self.building = True
		self.objects.power_button_action.set_active(
			ACTIONS.index(self.VeraPowerManager.GetHandlePowerKey())
		)
		self.objects.lid_switch_action.set_active(
			ACTIONS.index(self.VeraPowerManager.GetHandleLidSwitch())
		)
		self.building = False
	
	def on_scene_asked_to_close(self):
		"""
		Fired when the scene has been asked to close.
		"""
		
		# Close dbus connection
		self.bus_cancellable.cancel()
		
		return True

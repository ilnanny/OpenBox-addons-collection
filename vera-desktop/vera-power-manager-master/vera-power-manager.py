#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# vera-power-manager - DBus interface to logind's settings
# Copyright (C) 2014  Eugenio "g7" Paolantonio
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Authors:
#    Eugenio "g7" Paolantonio <me@medesimo.eu>
#

import sys

import os

import configparser

import subprocess

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from gi.repository import GLib, Polkit

TIMEOUT_LENGTH = 5 * 60

class Backlight:
	"""
	A representation of a Backlight device.
	"""
	
	step = 5
	useful_minimum_percentage = 1
	
	def __init__(self, name):
		"""
		Initializes the class.
		"""
		
		self.name = name
		self.path = os.path.join("/sys/class/backlight", self.name)
		
		# Save the maximum brightness level
		with open(os.path.join(self.path, "max_brightness")) as f:
			self.maximum = int(f.readline().strip())
		
	@property
	def current(self):
		"""
		Returns the current brightness level of the device.
		"""
		
		with open(os.path.join(self.path, "brightness")) as f:
			return int(f.readline().strip())
	
	@property
	def current_percentage(self):
		"""
		Returns the current brightness level, in percentage form.
		"""
		
		return int((100*self.current)/self.maximum)
	
	def _set(self, new_value):
		"""
		Sets the given value as the new brightness
		"""
		
		if new_value > self.maximum:
			new_value = self.maximum
		elif new_value < 0:
			new_value = 0
		
		with open(os.path.join(self.path, "brightness"), "w") as f:
			f.write(str(int(new_value)) + "\n")
	
	def set(self, new_value):
		"""
		Sets the given value as the new brightness.
		"""
		
		return self._set(
			int((self.maximum*new_value)/100.0)
			if not new_value == 100
			else self.maximum
		)
	
	def increase(self):
		"""
		Increases the backlight of self.step%.
		"""
		
		return self.set(self.current_percentage + self.step)
	
	def decrease(self):
		"""
		Decreases the backlight of self.step%.
		"""

		return self.set(
			(self.current_percentage - self.step)
			if self.current_percentage > self.step + self.useful_minimum_percentage
			else self.useful_minimum_percentage
		)

class Service(dbus.service.Object):
	"""
	The DBus service.
	"""
	
	# We can't link methods that still aren't created, so
	# we use strings to specify the "test"-function that will
	# validate the value before Set()'s daughter does the job.
	# This is pretty ugly, but it's better than to move this downside or,
	# worse, creating another dictionary.
	# This breaks lambdas, but I'll think about that when I'll actually
	# need them here ;)
	properties = {
		"HandlePowerKey" : ("s", "poweroff", "keys_check"),
		"HandleLidSwitch" : ("s", "suspend", "keys_check"),
		"HandleSuspendKey" : ("s", "suspend", "keys_check"),
		"HandleHibernateKey" : ("s", "hibernate", "keys_check"),
		"PowerKeyIgnoreInhibited" : ("b", False, None),
		"SuspendKeyIgnoreInhibited": ("b", False, None),
		"HibernateKeyIgnoreInhibited" : ("b", False, None),
		"LidSwitchIgnoreInhibited" : ("b", True, None),
		"IdleAction" : ("s", "ignore", "keys_check"),
		"IdleActionSec" : ("s", "30min", None), # FIXME
	}
	
	@dbus.service.signal(
		"org.semplicelinux.vera.powermanager",
		signature="i"
	)
	def BrightnessChanged(self, level):
		"""
		Signal emitted when the brightness level has been changed.
		"""
		
		pass
	
	def keys_check(self, value):
		"""
		Returns True if the value is suitable for usage in the
		Handle*Key/Switch keys.
		"""
		
		return value in (
			"ignore", "poweroff", "reboot", "halt", "kexec",
			"suspend", "hibernate", "hybrid-sleep", "lock"
		)
	
	def outside_timeout(*args, **kwargs):
		"""
		Decorator that ensures that the timeout doesn't elapse in the
		middle of our work.
		
		This mess of nested functions is needed because is not possible
		to use another decorator with @dbus.service.method. [1]
		We are then manually wrapping our decorator to python3-dbus's.
		
		[1] https://www.libreoffice.org/bugzilla/show_bug.cgi?id=22409
		"""
				
		def my_shiny_decorator(func):
		
			# Wrap the function around dbus.service.method
			func = dbus.service.method(*args, **kwargs)(func)
			
			def wrapper(self, *args, **kwargs):
				
				self.remove_timeout()
				result = func(self, *args, **kwargs)
				self.add_timeout()
				
				return result
			
			# Merge metadata, otherwise the method would not be
			# introspected
			wrapper.__name__ = func.__name__
			wrapper.__dict__.update(func.__dict__)
			wrapper.__module__ = wrapper.__module__
			
			return wrapper
		
		return my_shiny_decorator
	
	def Set(key):
		"""
		Given a key, returns a method that when called will set its value.
		"""
		
		def __set(self, new, user_interaction, sender=None, connection=None):
			"""
			Sets the value of the key to "new".
			
			Returns True if everything succeeded, False if something
			went wrong.
			"""			
			
			if None in (sender, connection):
				# This should not happen, sender and connection are both
				# required but are auto-populated by dbus' decorators.
				raise Exception("E: whaaat?")
			
			if not self.is_authorized(sender, connection, "org.semplicelinux.vera.powermanager.modify-logind", user_interaction):
				raise Exception("E: Not authorized")

			try:
				# Check value
				if self.properties[key][2] and not getattr(self, self.properties[key][2])(new):
					# Not a valid value
					return False
				
				# Handle booleans
				if self.properties[key][0] == "b":
					new = "yes" if new else "no"
				
				self.configuration["Login"][key] = new
				self.save()
			except:
				return False
			
			return True
		
		__set.__name__ = "Set%s" % key
		return __set
	
	def Get(key):
		"""
		Given a key, returns a method that when called will return its value.
		"""
		
		def __get(self):
			"""
			Returns the value of the given key, or a fallback.
			"""
			
			result = self.configuration.get("Login", key, fallback=self.properties[key][1])
			
			# Handle booleans
			if self.properties[key][0] == "b":
				result = True if result in ("yes", True) else False

			return result
		
		__get.__name__ = "Get%s" % key
		return __get
	
	@outside_timeout(
		"org.semplicelinux.vera.powermanager",
		out_signature="b"
	)
	def IsBacklightSupported(self):
		"""
		Returns True if vera-power-manager detected a backlight device,
		False if not.
		"""
		
		return (self.backlight != None)
	
	@outside_timeout(
		"org.semplicelinux.vera.powermanager",
		out_signature="i",
	)
	def GetCurrentBrightness(self):
		"""
		Returns the current brightness level.
		"""
		
		return 100 if not self.backlight else self.backlight.current_percentage
	
	@outside_timeout(
		"org.semplicelinux.vera.powermanager"
	)
	def IncreaseBrightness(self):
		"""
		Increases the brightness level.
		"""
		
		if self.backlight:
			self.backlight.increase()
			
			# Emit signal
			self.BrightnessChanged(self.backlight.current_percentage)
	
	@outside_timeout(
		"org.semplicelinux.vera.powermanager"
	)
	def DecreaseBrightness(self):
		"""
		Decreases the brightness level.
		"""
		
		if self.backlight:
			self.backlight.decrease()
			
			# Emit signal
			self.BrightnessChanged(self.backlight.current_percentage)
	
	@outside_timeout(
		"org.semplicelinux.vera.powermanager",
		in_signature="i"
	)
	def SetBrightness(self, new_value):
		"""
		Sets the given brightness level.
		"""
		
		if self.backlight: self.backlight.set(new_value)
	
	@outside_timeout(
		"org.semplicelinux.vera.powermanager",
		out_signature="i"
	)
	def GetBrightness(self):
		"""
		Returns the current brightness level.
		"""
		
		return 100 if not self.backlight else self.backlight.current_percentage
	
	def on_timeout_elapsed(self):
		"""
		Fired when the timeout elapsed.
		"""
		
		self.mainloop.quit()
		
		return False
	
	def remove_timeout(self):
		"""
		Removes the timeout.
		"""

		if self.timeout > 0:
			# Timeout already present, cancel it
			GLib.source_remove(self.timeout)
	
	def add_timeout(self):
		"""
		Timeout.
		"""
		
		self.timeout = GLib.timeout_add_seconds(TIMEOUT_LENGTH, self.on_timeout_elapsed)

	def __new__(cls):
		"""
		Class constructor.
		
		This method dynamically generates setters and getters from class' specified
		properties.
		"""
		
		# Generate setters and getters from cls.properties
		for prop in cls.properties:
			setattr(
				cls,
				"Set%s" % prop,
				cls.outside_timeout(
					"org.semplicelinux.vera.powermanager",
					in_signature="%sb" % cls.properties[prop][0],
					out_signature="b",
					sender_keyword="sender",
					connection_keyword="connection",
				)(cls.Set(prop)),
			)
			
			setattr(
				cls,
				"Get%s" % prop,
				cls.outside_timeout(
					"org.semplicelinux.vera.powermanager",
					out_signature=cls.properties[prop][0]
				)(cls.Get(prop)),
			)
			
			if not "org.semplicelinux.vera.powermanager" in cls._dbus_class_table["__main__.Service"]:
				cls._dbus_class_table["__main__.Service"]["org.semplicelinux.vera.powermanager"] = {}
			
			for method in ("Set%s" % prop, "Get%s" % prop):
				# Update dbus' class table so that when Introspecting the newly
				# added methods are properly detected
				cls._dbus_class_table["__main__.Service"]["org.semplicelinux.vera.powermanager"][method] = getattr(cls, method)
		
		# Business as usual
		return super().__new__(cls)
	
	def __init__(self):
		"""
		Initialization.
		"""
		
		self.timeout = 0
		
		self.mainloop = None
		
		self.backlight = None

		self.configuration = configparser.ConfigParser()
		self.configuration.optionxform = str # We want case-sensitiveness		
		self.configuration.read("/etc/systemd/logind.conf")
		
		self.bus_name = dbus.service.BusName("org.semplicelinux.vera.powermanager", bus=dbus.SystemBus())
		
		self.add_timeout()
		
		# Get polkit authority
		self.authority = Polkit.Authority.get_sync()
		
		# Backlight devices
		if os.path.exists("/sys/class/backlight"):
			backlight_devices = os.listdir("/sys/class/backlight")
			backlight = None
			# Current we can handle only one
			if len(backlight_devices) > 1 and "intel_backlight" in backlight_devices:
				# Pick "intel_backlight"
				backlight = "intel_backlight"
			elif len(backlight_devices) > 0:
				# Pick the first device
				backlight = backlight_devices[0]
			
			# Generate backlight object
			if backlight: self.backlight = Backlight(backlight)
		
		super().__init__(self.bus_name, "/org/semplicelinux/vera/powermanager")
	
	def start_mainloop(self):
		"""
		Creates and starts the main loop.
		"""
		
		self.mainloop = GLib.MainLoop()
		self.mainloop.run()
	
	def is_authorized(self, sender, connection, privilege, user_interaction=True):
		"""
		Checks if the sender has the given privilege.
		
		Returns True if yes, False if not.
		"""
		
		if not user_interaction:
			flags = Polkit.CheckAuthorizationFlags.NONE
		else:
			flags = Polkit.CheckAuthorizationFlags.ALLOW_USER_INTERACTION
		
		# Get PID
		pid = dbus.Interface(
			dbus.SystemBus().get_object(
				"org.freedesktop.DBus",
				"/org/freedesktop/DBus"
			),
			"org.freedesktop.DBus"
		).GetConnectionUnixProcessID(sender)
		
		try:
			result = self.authority.check_authorization_sync(
				Polkit.UnixProcess.new(pid),
				privilege,
				None,
				flags,
				None
			)
		except:
			return False
		
		return result.get_is_authorized()
	
	def save(self):
		"""
		Saves the configuration.
		"""
		
		with open("/etc/systemd/logind.conf", "w") as f:
			self.configuration.write(f)
		
		# Reload logind
		subprocess.Popen(["systemctl", "restart", "systemd-logind.service"])

if __name__ == "__main__":	
	DBusGMainLoop(set_as_default=True)
	service = Service()
	
	# Ladies and gentlemen...
	service.start_mainloop()

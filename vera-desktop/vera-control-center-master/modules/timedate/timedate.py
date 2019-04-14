# -*- coding: utf-8 -*-
#
# timedate - Time & Date module for Vera Control Center
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

from gi.repository import GLib, Gtk, Gdk, Gio, GObject, Pango

from veracc.widgets.UnlockBar import UnlockBar, ActionResponse

from keeptalking2.TimeZone import TimeZone

import quickstart
import datetime, time

BUS_NAME = "org.freedesktop.timedate1"

# On the {hours,minutes,seconds,date}_input boolean variables:
# As there isn't a reliable way to check if a GtkSpinbutton has been
# changed by the user or programmatically, we need to use those variables
# to block or allow the set_time() call.
#
# This should be classified as FIXME, it really needs a better handling
# if the toolkit will allow us to do something.

# FIXME: Focus on select_timezone_dialog

@quickstart.builder.from_file("./modules/timedate/timedate.glade")
class Scene(quickstart.scenes.BaseScene):
	"""
	Time & Date settings.
	"""
	
	events = {
		"delete-event" : ("select_timezone_dialog",),
		"realize": ("select_timezone_dialog",),
		"button-press-event" : ("main",),
		"clicked" : ("time_button", "location_button", "apply_timezone"),
		"toggled" : ("calendar_button", "ntp_enabled"),
		"value-changed" : ("hours_adjustment", "minutes_adjustment", "seconds_adjustment"),
		"wrapped" : ("hours",),
		"output" : ("hours", "minutes", "seconds")
	}
	
	@quickstart.threads.on_idle
	def build_timezone_list(self):
		"""
		Builds the timezone list.
		"""
		
		self.objects.timezones.clear()
		
		for item, key in self.TimeZone.supported.items():
			for zone in key:
				zone1 = "%s/%s" % (item, zone)
				itr = self.objects.timezones.append([zone1, zone])
				
				# Save the iter if it's the default
				if zone1 == self.TimeZone.default:
					# save the iter! ;)
					self.default = itr
		
		if self.default:
			sel = self.objects.timezone_treeview.get_selection()
			sel.select_iter(self.default)
			
			GObject.idle_add(self.objects.timezone_treeview.scroll_to_cell, sel.get_selected_rows()[1][0])
		
		GObject.idle_add(self.objects.timezone_treeview.grab_focus)
	
	def on_apply_timezone_clicked(self, button):
		"""
		Fired when the apply_timezone button has been clicked.
		"""
		
		GObject.idle_add(self.objects.select_timezone_dialog.hide)
		
		# Get selected
		sel = self.objects.timezone_treeview.get_selection()
		if not sel: return
		
		model, itr = sel.get_selected()
		if not itr: return
		
		selected = self.objects.timezones.get_value(itr, 0)
		if selected == self.objects.location_button.get_label(): return # Ugly!
		
		try:
			self.TimeDate.SetTimezone(
				'(sb)',
				selected,
				True
			)
			
			self.default = itr
			self.current_datetime = datetime.datetime.now()
		except:
			sel.select_iter(self.default)
		
		self.objects.location_button.set_label(self.objects.timezones.get_value(self.default, 0))
	
	def on_select_timezone_dialog_realize(self, widget):
		"""
		Fired when the select_timezone_dialog is going to be shown.
		"""
		
		self.build_timezone_list()
	
	def on_select_timezone_dialog_delete_event(self, widget, event):
		"""
		Fired when the select_timezone_dialog is going to be destroyed.
		"""
		
		widget.hide()
		
		return True # do not destroy
	
	def on_main_button_press_event(self, eventbox, event):
		"""
		Fired when the user has clicked on the eventbox.
		
		We use this call to return to the 'read-only' mode on the time
		view.
		"""
		
		if self.objects.time_modify.props.visible and event.type == Gdk.EventType.BUTTON_PRESS:
			self.refresh_infos()
			self.objects.time_modify.hide()
			self.objects.time_button.show()
	
	def on_spinbutton_output(self, spinbutton):
		"""
		Fired when a spinbutton has been changed.
		
		We use this method to ensure to have two digits everytime.
		Code comes from http://stackoverflow.com/a/9998968 (thanks!)
		
		(not connected to anything, due to a current limitation of quickstart
		we will associate on_*widget*_output to this method later)
		"""
		
		spinbutton.set_text('{:02d}'.format(int(spinbutton.get_adjustment().get_value())))
		
		return True

	on_hours_output = on_spinbutton_output
	on_minutes_output = on_spinbutton_output
	on_seconds_output = on_spinbutton_output
	
	def on_hours_wrapped(self, spinbutton):
		"""
		Fired when the hours spinbutton has been wrapped.
		"""
				
		if self.timezone12:
			if int(spinbutton.get_text()) == 1:
				# +1
				self.hour_offset = 0 if self.hour_offset == 12 else 12
			else:
				# -1
				self.hour_offset = 12 if self.hour_offset == 0 else 0
			
			# Reset time
			self.on_hours_adjustment_value_changed(spinbutton.get_adjustment())
	
	def set_time(self):
		"""
		Actually sets the time.
		"""
		
		print("Setting time...")
		
		self.TimeDate.SetTime('(xbb)', time.mktime(self.current_datetime.timetuple()) * 1000000, False, False)
		
	def on_hours_adjustment_value_changed(self, adjustment):
		"""
		Fired when the hours adjustment has been changed.
		"""
		
		if self.hours_input:
			value = int(adjustment.get_value())
			if self.timezone12:
				value += self.hour_offset
			
			self.current_datetime = self.current_datetime.replace(
				hour=value if not self.timezone12 else (
					0 if value == 24 else value
				)
			)
			if self.timezone12:
				self.objects.timezone12_edit.set_text(self.current_datetime.strftime("%p"))
			
			self.set_time()
			
					
	def on_minutes_adjustment_value_changed(self, adjustment):
		"""
		Fired when the minutes adjustment has been changed.
		"""
		
		if self.minutes_input:
			self.current_datetime = self.current_datetime.replace(minute=int(adjustment.get_value()))
			self.set_time()
			

	def on_seconds_adjustment_value_changed(self, adjustment):
		"""
		Fired when the seconds adjustment has been changed.
		"""
		
		if self.seconds_input:
			self.current_datetime = self.current_datetime.replace(second=int(adjustment.get_value()))
			self.set_time()
	
	def on_location_button_clicked(self, button):
		"""
		Fired when the location_button has been clicked.
		"""

		GObject.idle_add(self.objects.select_timezone_dialog.present)		
	
	def on_time_button_clicked(self, button):
		"""
		Fired when the time_button has been clicked.
		"""
		
		self.hours_input = self.minutes_input = self.seconds_input = False
		
		button.hide()
		self.objects.time_modify.show()
				
		# Load the adjustments with current data
		time = self.current_datetime.time()
		# Handle 12-hour timezones
		if not self.timezone12:
			# 24 hour
			self.objects.hours_adjustment.set_value(time.hour)
			self.objects.timezone12_edit.hide()
		else:
			# 12 hour
			self.objects.hours_adjustment.set_value(int(time.strftime("%I")))
			self.objects.timezone12_edit.set_text(self.current_datetime.strftime("%p"))
		self.objects.minutes_adjustment.set_value(time.minute)
		self.objects.seconds_adjustment.set_value(time.second)
	
	def on_calendar_button_toggled(self, button):
		"""
		Fired when the calendar_button has been toggled.
		"""
				
		if button.get_active(): self.calendar_popover.show_all()
	
	def on_day_selected(self, calendar):
		"""
		Fired when a day in the calendar has been selected.
		"""
		
		date = calendar.get_date()
		self.current_datetime = self.current_datetime.replace(
			year=date[0],
			month=date[1]+1,
			day=date[2]
		)
		
		self.objects.calendar_button.set_label(self.current_datetime.date().strftime("%A %d %B %Y"))
		
		# Update time if we should
		if self.date_input:
			self.set_time()
	
	def on_ntp_enabled_toggled(self, checkbox):
		"""
		Fired when the ntp_enabled checkbox has been toggled.
		"""
		
		if self.unlockbar.current_state == ActionResponse.UNLOCK:
			print("Setting NTP to %s" % checkbox.get_active())
			try:
				self.TimeDate.SetNTP('(bb)', checkbox.get_active(), False)
			except GLib.GError as error:
				# FIXME? Here it raises FileNotFound error, I think
				# is some Debian bug?
				pass
		
		# Set sensitivity on the manual container
		self.objects.manual_container.set_sensitive(not checkbox.get_active())
	
	@quickstart.threads.on_idle
	def refresh_infos(self):
		"""
		Refreshes the information displayed.
		"""
		
		_datetime = datetime.datetime.now()
		
		self.objects.time.set_text(_datetime.time().strftime("%X"))
	
	@quickstart.threads.on_idle
	def update_date(self):
		"""
		Updates the date.
		"""
		
		date = self.current_datetime.date()
		
		self.date_input = False
		self.calendar.select_month(date.month-1, date.year)
		self.calendar.select_day(date.day)
		self.date_input = True
	
	@quickstart.threads.on_idle
	def update_time(self):
		"""
		Updates the time.
		"""
		
		self.current_datetime += datetime.timedelta(seconds=1)
		
		time = self.current_datetime.time()
		if time.hour == 00 and time.minute == 00 and time.second == 00:
			# Day changed
			self.update_date()
		
		# Update the current visible time object
		if self.objects.time_modify.props.visible:
			if time.minute == 00 and time.second == 00: 
				self.hours_input = False
				self.objects.hours_adjustment.set_value(time.hour)
			if time.second == 00:
				self.minutes_input = False
				self.objects.minutes_adjustment.set_value(time.minute)
			self.seconds_input = False
			self.objects.seconds_adjustment.set_value(time.second)
			
			self.hours_input = self.minutes_input = self.seconds_input = True
		else:
			self.objects.time.set_text(time.strftime("%X"))
	
	def on_locked(self, unlockbar):
		"""
		Fired when the user (or policykit) has locked the special
		temporary privilegies.
		"""
		
		# Locked, disable sensitivity on everything...
		self.objects.container.set_sensitive(False)
	
	def on_unlocked(self, unlockbar):
		"""
		Fired when the user has got the special temporary privilegies.
		"""
		
		# Unlocked, re-set sensitivity
		self.objects.container.set_sensitive(True)
		
			
	def prepare_scene(self):
		"""
		Called when doing the scene setup.
		"""
		
		self.scene_container = self.objects.main
		
		self.default = None
		
		self.TimeZone = TimeZone()
		self.hour_offset = 0
		self.timezone12 = None
		
		# Create unlockbar
		self.unlockbar = UnlockBar("org.freedesktop.timedate1.set-time")
		self.unlockbar.connect("locked", self.on_locked)
		self.unlockbar.connect("unlocked", self.on_unlocked)
		self.objects.main_box.pack_start(self.unlockbar, False, False, 0)
		
		# Enter in the bus
		self.bus_cancellable = Gio.Cancellable()
		self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, self.bus_cancellable)
		self.TimeDate = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/timedate1",
			BUS_NAME,
			self.bus_cancellable
		)
		self.TimeDateProperties = Gio.DBusProxy.new_sync(
			self.bus,
			0,
			None,
			BUS_NAME,
			"/org/freedesktop/timedate1",
			"org.freedesktop.DBus.Properties",
			self.bus_cancellable
		) # Really we should create a new proxy to get the properties?!
		
		#self.refresh_infos()
		
		# Set-up select timezone dialog
		self.objects.timezone_treeview.append_column(
			Gtk.TreeViewColumn(
				"Timezone",
				Gtk.CellRendererText(),
				text=0
			)
		)
		self.objects.timezones.set_sort_column_id(0, Gtk.SortType.ASCENDING)
		
		# Create calendar popover
		self.calendar = Gtk.Calendar()
		self.calendar.connect("day-selected", self.on_day_selected)
		self.calendar_popover = Gtk.Popover.new(self.objects.calendar_button)
		self.calendar_popover.set_modal(True)
		self.calendar_popover.connect("closed", lambda x: self.objects.calendar_button.set_active(False))
		self.calendar_popover.add(self.calendar)
		
		# Set appropriate font size and weight
		context = self.objects.time.create_pango_context()
		desc = context.get_font_description()
		desc.set_weight(Pango.Weight.LIGHT) # Weight
		desc.set_size(Pango.SCALE*80) # Size
		
		self.objects.time.override_font(desc)
		self.objects.hours.override_font(desc)
		self.objects.minutes.override_font(desc)
		self.objects.seconds.override_font(desc)
		self.objects.timezone12_edit.override_font(desc)
		
		# Set mask on the main eventbox
		self.objects.main.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		
		# Styling
		self.objects.time_button.get_style_context().add_class("no-borders")
		self.objects.location_button.get_style_context().add_class("no-borders")
		self.objects.calendar_button.get_style_context().add_class("no-borders")
		
	
	def on_scene_called(self):
		"""
		Called when switching to this scene.
		
		We will handle here all timeouts to ensure we syncronize the
		time label with the actual time.
		"""

		self.objects.main.show_all()
		self.objects.time_modify.hide()
		
		# We are locked
		self.unlockbar.emit("locked")
		
		self.current_datetime = datetime.datetime.now()
		self.timezone12 = (not self.current_datetime.strftime("%p") == "")
		adj = self.objects.hours.get_adjustment()
		if self.timezone12:
			adj.set_upper(12)
			adj.set_lower(1)
		else:
			adj.set_upper(23)
			adj.set_lower(0)
		if self.current_datetime.time().hour > 12: self.hour_offset = 12
			
		self.update_date()
		self.update_time()
		
		# NTP
		ntp = bool(self.TimeDateProperties.Get('(ss)', BUS_NAME, 'NTP'))
		self.objects.ntp_enabled.set_active(ntp)
		
		# Timezone
		self.objects.location_button.set_label(self.TimeDateProperties.Get('(ss)', BUS_NAME, 'Timezone'))
		
		self.label_timeout = GLib.timeout_add_seconds(1, self.update_time)
	
	def on_scene_asked_to_close(self):
		"""
		Do some cleanup before returning home
		"""
		
		GLib.source_remove(self.label_timeout)
		self.unlockbar.cancel_authorization()
		
		self.bus_cancellable.cancel()
		
		return True
		

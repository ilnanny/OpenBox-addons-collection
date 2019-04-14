#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

import dbus
import os

class TestWindow:


    @property
    def _sysbus (self):
        """System DBus"""
        if not hasattr (TestWindow, "__sysbus"):
            TestWindow.__sysbus = dbus.SystemBus ()
        return TestWindow.__sysbus

    @property
    def _sessbus (self):
        """Session DBus"""
        if not hasattr (TestWindow, "__sessbus"):
            TestWindow.__sessbus = dbus.SessionBus ()
        return TestWindow.__sessbus

    @property
    def _polkit (self):
        """PolicyKit object"""
        if not hasattr (TestWindow, "__polkit"):
            pk = self._sysbus.get_object ("org.freedesktop.PolicyKit", "/")
            TestWindow.__polkit = dbus.Interface(pk, 'org.freedesktop.PolicyKit')
        return TestWindow.__polkit

    @property
    def _halpm (self):
        """HAL controller object""" 
        if not hasattr (TestWindow, "__halpm"):
            hal = self._sysbus.get_object ("org.freedesktop.Hal", "/org/freedesktop/Hal/devices/computer")
            TestWindow.__halpm  = dbus.Interface(hal, "org.freedesktop.Hal.Device.SystemPowerManagement")
        return TestWindow.__halpm

    @property
    def _authagent (self):
        """AuthenticationAgent object"""
        if not hasattr (TestWindow, "__authagent"):
            autha = self._sessbus.get_object ("org.freedesktop.PolicyKit.AuthenticationAgent", "/", "org.gnome.PolicyKit.AuthorizationManager.SingleInstance")
            TestWindow.__authagent = dbus.Interface(autha,'org.freedesktop.PolicyKit.AuthenticationAgent')
        return TestWindow.__authagent
    


    def on_button_clicked(self, widget, data=None):

	#Call the D-Bus method to request PolicyKit authorization:

        gdkwindow = self.window.window
        xid = gdkwindow.xid

        print "Calling ObtainAuthorization..."

        granted = self._authagent.ObtainAuthorization("org.freedesktop.hal.power-management.reboot-multiple-sessions", xid, os.getpid())

        print "...Finished."
        print "granted=", granted

        print "isauthorized=", self._polkit.IsProcessAuthorized("org.freedesktop.hal.power-management.reboot-multiple-sessions", os.getpid(), False)


        print self._halpm.Reboot()

    def on_delete_event(self, widget, event, data=None):
        # Close the window:
        return False

    def on_destroy(self, widget, data=None):
        gtk.main_quit()

    def show(self):
       self.window.show()

    def __init__(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.on_delete_event)
        self.window.connect("destroy", self.on_destroy)

        self.button = gtk.Button("Obtain Authorization")
        self.button.connect("clicked", self.on_button_clicked, None)
        self.window.add(self.button)
        self.button.show()

window = TestWindow()
window.show()
gtk.main()


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

from distutils.core import setup

setup(
	name='vera-power-manager',
	version='1.0.4',
	description="DBus interface to logind's settings",
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='http://github.com/vera-desktop/vera-power-manager',
	scripts=["vera-power-manager.py"],
	data_files=[
		("/etc/dbus-1/system.d", ["data/org.semplicelinux.vera.powermanager.conf"]),
		("/usr/share/dbus-1/system-services", ["data/org.semplicelinux.vera.powermanager.service"]),
		("/usr/share/polkit-1/actions", ["data/org.semplicelinux.vera.powermanager.policy"]),
		("/etc/acpi/events", ["acpid/vera-power-manager-brightnessdown", "acpid/vera-power-manager-brightnessup"])
	],
	# package_dir={'bin':''},
	requires=['dbus', 'gi.repository.GLib', 'gi.repository.Polkit', 'gi.repository.Gio', 'time', 'configparser', 'os', 'sys', 'subprocess'],
)

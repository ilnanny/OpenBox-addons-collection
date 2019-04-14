#!/usr/bin/python3
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
from distutils.core import setup, Command
from distutils.command.build import build
from distutils.command.install import install

import subprocess
import shutil

data_path = "/usr/share/vera-control-center"
l10n_path = "./po"

APP_NAME = "vera-control-center"

class CreatePotTemplate(Command):
	"""
	Creates a .pot template.
	"""
	
	description = "creates a .pot localization template from the program sources."
	user_options = []
	
	def initialize_options(self):
		"""
		Initialize options
		"""
		
		self.cwd = None
	
	def finalize_options(self):
		"""
		Finalize options
		"""
		
		self.cwd = os.getcwd()
	
	def run(self):
		"""
		Does things.
		"""
		
		assert os.getcwd() == self.cwd, "You must be in the package root: %s" % self.cwd
		
		py_files = []
		glade_files = []
		desktop_files = []
		
		for directory, dirnames, filenames in os.walk("."):
			for file_ in filenames:
				if file_.endswith(".py"):
					py_files.append(os.path.join(directory, file_))
				elif file_.endswith(".glade"):
					glade_files.append(os.path.join(directory, file_))
				elif file_.endswith(".desktop"):
					desktop_files.append(os.path.join(directory, file_))
					
		subprocess.call([
			"xgettext",
			"--language=Python",
			"--from-code=utf-8",
			"--keyword=_",
			"--output=%s" % os.path.join(self.cwd, l10n_path, APP_NAME, "%s.pot" % APP_NAME),
		] + py_files)
		
		subprocess.call([
			"xgettext",
			"--language=Desktop",
			"--from-code=utf-8",
			"-j",
			"--output=%s" % os.path.join(self.cwd, l10n_path, APP_NAME, "%s.pot" % APP_NAME)
		] + desktop_files)
		
		for file_ in glade_files:
			subprocess.call([
				"intltool-extract",
				"--type=gettext/glade",
				file_
			])
			subprocess.call([
				"xgettext",
				"--from-code=utf-8",
				"--language=C",
				"--keyword=N_",
				"-j",
				"--output=%s" % os.path.join(self.cwd, l10n_path, APP_NAME, "%s.pot" % APP_NAME),
				"-j",
				file_ + ".h"
			])
			os.remove(file_ + ".h")
		
#find . -name "*.py" | xgettext --language=Python --keyword=_ --output=po/$APP_NAME/$APP_NAME.pot -f -
#
# Find and extract from glade files
#files=$(find . -name "*.glade")
#for glade in $files; do
#	intltool-extract --type=gettext/glade $glade
#	xgettext --language="C" --keyword=N_ -j --output=po/$APP_NAME/$APP_NAME.pot -j ${glade}.h
#	rm ${glade}.h
#done


class CustomBuild(build):
	"""
	Hooks.
	"""
	
	def run(self):
		"""
		Runs the installation.
		"""
		
		super().run()
		
		# Build mos
		for directory, dirnames, filenames in os.walk(l10n_path):
			for file_ in filenames:
				if file_.endswith(".po"):
					source = os.path.join(directory, file_)
					target_dir = os.path.join("./build", directory)
					target = os.path.join(target_dir, file_.replace(".po",".mo"))
					
					if not os.path.exists(target_dir):
						os.makedirs(target_dir)
					
					print("Compiling translation %s" % file_)
					subprocess.call(["msgfmt", "--output-file=%s" % target, source])

class CustomInstall(install):
	"""
	Hooks.
	"""
	
	def run(self):
		"""
		Runs the installation.
		"""
		
		super().run()
		
		# Install mos
		for directory, dirnames, filenames in os.walk(os.path.join("./build", l10n_path)):
			for file_ in filenames:
				if file_.endswith(".mo"):
					source = os.path.join(directory, file_)
					target_dir = os.path.join(
						self.root if self.root else "/",
						"usr/share/locale",
						file_.replace(".mo",""),
						"LC_MESSAGES"
					)
					target = os.path.join(target_dir, os.path.basename(directory) + ".mo")
					
					if not os.path.exists(target_dir):
						os.makedirs(target_dir)
					
					shutil.copyfile(source, target)
					os.chmod(target, 644)


def get_module_files():
	"""
	Walks around modules/ to get non-python files that need to be specified
	in data_files.
	"""
	
	data_files = []
	
	for directory, dirnames, filenames in os.walk("./modules"):
		this_dir = [os.path.join(data_path, directory), []]
		
		for file_ in filenames:
			if not file_.endswith(".py") and not file_.endswith(".pyc"):
				this_dir[-1].append(os.path.join(directory, file_))
		
		if this_dir[-1]: data_files.append(tuple(this_dir))
	
	return data_files

data_files = get_module_files()
data_files += [
	(data_path, ["controlcenterui.glade", "veracc.css"]),	
]

setup(
	cmdclass={
		"pot": CreatePotTemplate,
		"build": CustomBuild,
		"install": CustomInstall
	},
	name='vera-control-center',
	version='1.0.21',
	description='Simple, fast and modular control center for the Vera Desktop Environment',
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='https://github.com/vera-desktop/vera-control-center',
	scripts=['vera-control-center.py'],
	packages=[
		'veracc',
		'veracc.widgets',
		
		'modules',
		'modules.timedate',
		'modules.theme',
		'modules.theme.pages',
		'modules.tint2',
		'modules.power',
		'modules.networkmanager',
		'modules.desktop',
		'modules.about',
		'modules.autostart',
		'modules.locale',
		'modules.keyboard',
		'modules.shortcuts',
		'modules.usersadmin',
	],
	data_files=data_files,
	requires=[
		'os',
		'gi.repository.Gtk',
		'gi.repository.Gio',
		'gi.repository.GObject',
		'gi.repository.GLib',
		'gi.repository.GdkPixbuf',
		'gi.repository.Polkit',
		'keeptalking2',
		'quickstart',
		'collections.OrderedDict',
		'subprocess',
		'enum',
		'xdg',
		'datetime',
		'time',
	],
)

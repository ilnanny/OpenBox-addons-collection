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

import os

import re

class OsRelease(dict):
	"""
	An interface to the {/etc,/usr/lib}/os-release contents.
	"""

	# Variables to export, with their default values
	exported_variables = {
		"NAME" : "Linux",
		"VERSION" : None,
		"ID" : "linux",
		"ID_LIKE" : None,
		"VERSION_ID" : None,
		"PRETTY_NAME" : "Linux",
		"ANSI_COLOR" : None,
		"CPE_NAME" : None,
		"HOME_URL" : None,
		"SUPPORT_URL" : None,
		"BUG_REPORT_URL" : None,
		"PRIVACY_POLICY_URL" : None,
		"BUILD_ID" : None,
		"VARIANT" : None,
		"VARIANT_ID" : None,
	}

	def __init__(self, try_list=["/etc/os-release","/usr/lib/os-release"]):
		"""
		Initializes the class.

		`try_list` it's a list of files to try to read from. Default
		is ["/etc/os-release", "/usr/lib/os-release"].
		"""

		super().__init__()

		# Compile regular expressions
		self.match_quotes = re.compile(r"^\"|\"$")
		self.capture_codename = re.compile(r"\((.+)\)")

		# Set default variables
		self.update(self.exported_variables)

		for file_to_try in try_list:
			if os.path.exists(file_to_try):
				self.parse_file(file_to_try)
				break

	def parse_file(self, os_release):
		"""
		Parses the file specifies in `os_release` and sets its contents
		in the dictionary.
		"""

		with open(os_release, "r") as f:
			for line in f:
				line = line.strip().split("=")

				if not len(line) > 1:
					# Not a variable declaration
					continue

				key = line[0].upper()
				if key in self.exported_variables:
					self[key] = self.match_quotes.sub("", "=".join(line[1:]))

	def __getattr__(self, attribute):
		"""
		Returns the specified key if it's in the exported_variables
		dictionary, otherwise raises an AttributeError.
		"""

		if attribute in self.exported_variables:
			return self[attribute]

		raise AttributeError("class has no attribute \"%s\"" % attribute)
	
	@property
	def SEMPLICE_CODENAME(self):
		"""
		Returns the Semplice codename, or an empty string if it can't
		be retrieved.
		"""

		match = self.capture_codename.search(self.PRETTY_NAME)
		if match and match.lastindex > 0:
			return match.group(match.lastindex)

		return ""

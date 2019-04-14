#!/usr/bin/python3
# -*- coding: utf-8 -*

"""
This script dumps translated strings from po files to the modules'
desktop entries.
"""

import os
import polib

from xdg.DesktopEntry import DesktopEntry

class TranslationCatalog:
	
	languages = {}
	
	def __init__(self, source_dir):
		"""
		Initializes the class.
		"""
		
		for translation in os.listdir(source_dir):
			
			if translation.endswith(".po"):
				language = translation.replace(".po","")
				self.languages[language] = polib.pofile(os.path.join(source_dir, translation))
				
catalog = TranslationCatalog("./po/vera-control-center")

# Search for desktop files
desktop_files = []

for directory, dirnames, filenames in os.walk("."):
	for file_ in filenames:
		if file_.endswith(".desktop"):
			entry = DesktopEntry(os.path.join(directory, file_))
			
			for key in ("Name", "Comment", "Keywords"):
				try:
					source = entry.get(key)
				except:
					continue
				
				for lang, obj in TranslationCatalog.languages.items():
					found = obj.find(source)
					if found and found.msgstr != "":
						# xdg's IniFile supports the locale= keyword,
						# but it supports only a boolean value. The locale
						# is hardcoded to the one of the current system.
						# We workaround this by specifying the right key
						# right now.
						entry.set("%s[%s]" % (key, lang), found.msgstr)
			
			entry.write()

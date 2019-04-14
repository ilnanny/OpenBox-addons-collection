#!/usr/bin/env python
# OpenBox pipe menu clipboard manager. Show parcellite clipboard, and inserts selected clip.
#
# Copyright 2013 Joe Bloggs (vapniks@yahoo.com)
#
# These scripts: ob_clipboard_manager.py, ob_clipboard_pipe_menu.py & ob_paste_clip.py
# create a pipe menu for openbox which will display the history of clippings stored by parcellite
# or clipit, and allow you to paste one of them by selecting it.
# Obviously either parcellite or clipit needs to be installed for this to work, and they should not
# be run in daemon mode.
# parcellite should be available from the usual repositories, and clipit can be
# obtained from here: http://clipit.rspwn.com/
# If clipit is used then any static clippings will also be displayed in the pipe menu.
# You may need to alter some of the following variables in ob_clipboard_manager.py:
# clipit_history_file, parcellite_history_file, max_displayed_items 

# Installation: copy ob_clipboard_manager.py, ob_clipboard_pipe_menu.py & ob_paste_clip.py to your openbox 
# config directory (on Ubuntu its ~/.config/openbox), then add an item to your openbox menu.xml file
# (also in the config dir) in the form:
#
#   <menu execute="~/.config/openbox/ob_clipboard_pipe_menu.py" id="clipboard" label="Clipboard"/>
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
#

import os
import struct
from xml.sax.saxutils import escape, XMLGenerator
from os.path import expanduser
import string
import subprocess
import re

# change the following paths if necessary
clipit_history_file = expanduser('~') + "/.local/share/clipit/history"
parcellite_history_file = expanduser('~') + "/.local/share/parcellite/history"
max_displayed_items = 20

class ob_cb_manager:
    def __init__(self): # constructor
        # create regexp for character replacement
        self.replacements = {'&':'&amp;','"':'&quot;','<':'&lt;','>':'&gt;',"'":'&apos;','_':'__','':' ','':' '}
        self.regexp = re.compile('|'.join(map(re.escape, self.replacements.keys())))
        self.ctrlchars = reduce(lambda x, y: type(x) is str and x + chr(y) or chr(x) + chr(y),range(33))
        # alter the following line if your history file is found elsewhere
        self.clippings = []
        self.running = False
        # find out which clipboard manager is running and read appropriate history file
        ps = subprocess.Popen("ps -ef | grep \"parcellite\|clipit\" | grep -v grep", shell=True, stdout=subprocess.PIPE)
        output = ps.stdout.read()
        ps.wait()
        if string.find(output,"clipit") != -1:
            # read the appropriate history file
            self.read_clipit_history(length=max_displayed_items, filepath=clipit_history_file)
            self.running = True
        elif string.find(output,"parcellite") != -1:
            self.read_parcellite_history(length=max_displayed_items, filepath=parcellite_history_file)
            self.running = True

    def read_parcellite_history(self, length=20, filepath=None):
        if filepath is None:
            filepath = parcellite_history_file
        self.clippings = []
        # open the file as binary
        f = open(filepath,"rb")
        # read the first 4 bytes (which should indicate the size of the first clipping)
        size = struct.unpack('i',f.read(4))[0]
        # stop when we have enough clippings or if we reach a clipping of length 0 
        count = 0
        while size != 0 and count < length:
            # read the clipping and append it to clippings
            self.clippings.append(f.read(size))
            count = count + 1
            # read the next 4 bytes
            data = f.read(4)
            # convert to a size, or quit if we've reached the end of the file
            if data:
                size = struct.unpack('i',data)[0]
            else:
                size = 0

    def read_clipit_history(self, length=20, filepath=None):
        if filepath is None:
            filepath = clipit_history_file
        volatile_clippings = []
        static_clippings = []
        # open the file as binary
        f = open(filepath,"rb")
        # save some typing with this subfunction
        def read4bytes():
            data = f.read(4)
            if data:
                return struct.unpack('i',data)[0]
            else:
                return 0
        # read the first 4 bytes (which should indicate the size of the first clipping)
        size = read4bytes()
        # if size = -1 we are using the new filetype introduced in 1.4.1
        if size == -1:
            # ignore the extra 64 bytes of initial data
            f.read(64)
            # read clippings until we reach the end
            size = read4bytes()
            data_type = read4bytes()
            while size and data_type:
                item = f.read(size)
                if data_type == 1:
                    clip = item
                elif data_type == 2: # FIXME!!!!!!!!!!
                    if not struct.unpack('i',item)[0]:
                        volatile_clippings.append(clip)
                    else:
                        static_clippings.append(clip)                        
                size = read4bytes()
                data_type = read4bytes()
            # take required number of volatile clippings and add static clippings to the end
            self.clippings = volatile_clippings[0:length] + static_clippings[0:length]
        # for versions of clipit prior to 1.4.1 the history file format is the same as parcellite
        else:
            self.read_parcellite_history(length, filepath)

            
    # print the pipe menu items
    def print_menu_items(self):
        if self.running:
            for i in range(0,len(self.clippings)):
                clip = self.clippings[i]
                # remove control characters 
                sanetext = clip[:50].translate(None,self.ctrlchars)
                # replace characters that cause problems in XML                
                sanetext = self.regexp.sub(lambda match: self.replacements[match.group(0)], sanetext)
                # add shortcut keys
                if i < 10:
                    shortcut = '_' + str(i) + ': '
                elif i < 10+26:
                    shortcut = '_' + string.ascii_lowercase[i-10] + ': '
                elif i < 36+26:
                    shortcut = '_' + string.ascii_uppercase[i-36] + ': '
                else:
                    shortcut = '   '
                thisdir = os.path.dirname(os.path.realpath(__file__))
                command = thisdir + "/ob_paste_clip.py " + str(i)
                print '<item label="' + shortcut + sanetext + '">\n<action name="execute"><execute>' + \
                    command + '</execute></action>\n</item>'
        else:
            print '<item label="You need to start parcellite or clipit for this to work!">\n</item>'
            print '<item label="(without daemon option)">\n</item>' 



            
#manager = ob_cb_manager()
#manager.read_clipit_history()

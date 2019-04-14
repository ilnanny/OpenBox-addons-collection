#!/usr/bin/env python
# OpenBox pipe menu to show currently defined openbox keybindings, and edit them.
#
# Copyright 2010 Joe Bloggs (vapniks@yahoo.com)
#
# Installation: copy this file to your openbox config directory (on Ubuntu its ~/.config/openbox),
# then add an item to your openbox menu.xml file (also in the config dir) in the form:
#
#   <menu execute="~/.config/openbox/show_ob_keybindings.py" id="showkeys" label="Keybindings"/>
# 
# IMPORTANT: you need to change the rcfilepath variable to point to the xml file containing
# your openbox keybindings.
# Also, the default editor is set to emacsclient. If you want to use a different editor you need to
# change the editCommand function below.
#
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

import xml.parsers.expat
import re
from string import strip, replace, rjust
from xml.sax import make_parser
from xml.sax import saxutils
from xml.sax.handler import feature_namespaces
from os.path import expanduser

# following line needs to be set to point the xml file containing your openbox keybindings
rcfilepath = expanduser('~') + "/.config/openbox/rc.xml"

class rcHandler(saxutils.handler.ContentHandler): # handler class inherits from saxutils.DefaultHandler
    def __init__(self): # constructor 
        self.in_keybind = 0
        self.in_action = 0
        self.in_name = 0
        self.has_command = 0
        self.keybind = ''
        self.keybind2 = ''
        self.action = ''
        self.name = ''
        self.rcfile = rcfilepath
        self.replacements = {"C-":"Ctrl+","W-":"Windows+","S-":"Shift+","A-":"Alt+","M-":"Meta+","H-":"Hyper+"}
        self.regexp = re.compile('|'.join(map(re.escape, self.replacements.keys())))
    # this function should return a string containing the command you want to run for the current keybinding        
    def editCommand(self): 
        return 'emacsclient -a emacs -e \'(progn (find-file "' + self.rcfile + '") ' + \
            '(goto-char (point-min)) (re-search-forward "\\\"' + self.keybind + '\\\""))\''
        
    # override function from DefaultHandler, called at start of xml element
    def startElement(self, name, attrs):
        # start of <keybind ...> item
        if name == 'keybind':
            # Get the keybinding and perform replacements to make more readable
            self.keybind = attrs.get('key',None)
            self.keybind = self.regexp.sub(lambda match: self.replacements[match.group(0)], self.keybind)
            self.in_keybind += 1
            # append the keybinding text to self.keybind2 (could be a keychain)
            if self.in_keybind == 1:
                self.keybind2 = self.keybind
            else:
                self.keybind2 += "  " + self.keybind
        # start of <action ...> item within <keybind ...> item
        elif (name == 'action') and (self.in_keybind > 0):
            self.in_action = 1
            self.action = attrs.get('name', None)
        # start of <name> item within <keybind ...> item
        elif (name == 'name') and (self.in_keybind > 0):
            # reset "name" variable (it gets set by "characters" function)
            self.name = ''
            self.in_name = 1
        # start of <command> item
        elif (name == 'command'):
            self.has_command = 1
            
    # override function from DefaultHandler, called at end of xml element            
    def endElement(self, name):
        # end of </keybind> item
        if name == 'keybind':
            self.in_action = 0
            self.has_command = 0
            # remove last keybinding from the current keychain
            self.in_keybind -= 1
            self.keybind2 = re.sub("  [^ ]+$","",self.keybind2)
            # make sure we don't carry unused names across to next keybinding
            self.name = ''
        # end of </name> item
        elif (name == 'name'):
            self.in_name = 0
        # print menu item after end of </command> item (which is in a <keybind ...> item)
        elif (name == 'command') and self.in_keybind:
            print '<item label="' + self.keybind2 + rjust(strip(self.name),100) + \
                '">\n<action name="execute"><execute>' + self.editCommand() + '</execute></action>\n</item>'
            self.name = '' 
        # print menu item after end of </action> item (within <keybind ...> item)
        # unless a <command> item has already been printed
        elif (name =='action') and (self.in_keybind > 0) and (not self.has_command):
            # if there's no <name> item for this action, print the action name
            if self.name == '':
                print '<item label="' + self.keybind2 + rjust(self.action,100) + \
                  '">\n<action name="execute"><execute>' + self.editCommand() + '</execute></action>\n</item>'
            # otherwise print the <name>
            else:
                print '<item label="' + self.keybind2 + rjust(strip(self.name),100) + \
                  '">\n<action name="execute"><execute>' + self.editCommand() + '</execute></action>\n</item>'
                self.name = ''
                

    # override function from DefaultHandler, called as each character outside an xml tag is read
    def characters(self,ch):
        # only save chars within a <name> item
        if self.in_name:
            self.name = self.name + ch
            
if __name__ == '__main__':
    parser = make_parser() # create a parser
    parser.setFeature(feature_namespaces, 0) # tell parser we're not interested in XML namespaces
    dh = rcHandler() # create the document handler
    parser.setContentHandler(dh) # tell the parser to use our document handler
    print '<?xml version="1.0" encoding="UTF-8"?>' # header
    print '<openbox_pipe_menu>' # main pipe menu element
    print '<item label="Select a keybinding to edit it"></item>'
    parser.parse(dh.rcfile) # parse the rc.xml file
    print '</openbox_pipe_menu>\n' # end pipe menu element


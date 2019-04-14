#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------------------------

checkmail.py - version 8
by Vlad George

Please edit the ~/.checkmailrc file and read the README for further information.

Changelog:
    version 8: uses python's internal xml.etree.ElementTree - no need for separate python-elementree module
    version 7: added gmail/SSL support; filters URLs and opens them im browser
    version 6: added regex filter
    version 5: added mail content; set read flag
    version 4: added osdtoggle
    version 3: added pyosd stuff
    version 2: first working version

#-------------------------------------------------------------------------------

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
http://www.fsf.org/

"""

#-------------------------------------------------------------------------------
#                                   Script
#-------------------------------------------------------------------------------


# {{{ ##  fold markers start

class Mails(object):

    def __init__(self, server, user, password, mailbox):
        """ user mail stuff variables: """
        self.server = server
        self.user = user
        self.password = password
        self.mailbox = mailbox
        self.tmp_file = "/tmp/.mails." + server_name + "-" + str(os.getuid()) + ".cache"


    def __imapConnect(self, data_dict):
        """ access IMAP-server: input dict w/ deleted mails; output: dict w/ new mails """
        if connect_over_ssl != 0:
            m = imaplib.IMAP4_SSL(self.server)
        else:
            m = imaplib.IMAP4(self.server)
        m.login(self.user, self.password)
        m.select(self.mailbox)
        for i in data_dict.keys():
            if data_dict[i][3] == "deleted":
                m.store(i, "FLAGS", '\\Deleted')
            elif data_dict[i][3] == "seen":
                m.store(i, "FLAGS", '\\Seen')
        m.expunge()

        data_dict=dict()

        alt_1, unread = m.search(None,'(UNSEEN UNDELETED)')
        for num in unread[0].split() :
            alt_2, body = m.fetch(num,'(BODY[HEADER.FIELDS (DATE FROM SUBJECT)] BODY[TEXT])')
            body.remove(')')

            body_text = re.compile('^.*BODY\[TEXT\].*$')    ##  check for order of text and header, then sort 
            if body_text.match(body[0][0]) == None:         ##  first header[0], then text[1]
                data_1 = body[0][1].split('\r\n')
                data_2 = body[1][1].split('\n')
            else:                                           ##  first text[0], then header[1]
                data_1 = body[1][1].split('\r\n')
                data_2 = body[0][1].split('\n')
            data_1 = data_1[0:3]
            data_1.sort()     ##  Date, From, Subject

            data_3 = []     ##  mail content
            content_filter = re.compile('^Content-|--=20|>=20|.*charset|--Sig|-----', re.M)
            for i in data_2:
                if content_filter.match(i) == None:
                    data_3.append(unicode(i, 'latin-1'))
            data_3 = data_3[0:content_lines]
            del data_2
            try:
                data_dict[int(num)] = [data_1[0].split(': ',1)[1].rsplit('+')[0].rsplit('-')[0], data_1[1].split(':',1)[1], data_1[2].split(':',1)[1], '', data_3]
            except IndexError:
                pass
            m.store(num, "FLAGS", '(UNSEEN)')
        m.close()
        m.logout
        return data_dict


    def __xmlSegment(self, root, mail_num, value_list):
        """ main mail-menu -> mails arranged /new from -> /new subject /new date /new open in agent /new delete -> /new confirm /end
            {mail_num:[[0]-date,[1]-from,[2]-subject,[3]-[optional_read_flag | optional_deleted_flag], []xxx:[, , , ] , , ...} """
        menu = ET.SubElement(root, "menu", attrib = {"id" : str(mail_num) + "-menu", "label" : value_list[1]})
        date_entry = ET.SubElement(menu, "item", attrib = {"label": "date: " + value_list[0]})
        date_entry_action = ET.SubElement(date_entry, "action", attrib = {"name": "Execute"})
        date_entry_execute = ET.SubElement(date_entry_action, "command")
        date_entry_execute.text = "true"
        subject_menu = ET.SubElement(menu, "menu", attrib = {"id":str(mail_num) + "-subject-menu", "label": "subject: " + value_list[2]})
        grab_url = re.compile(r'((https?://|ftp://|www\.)[-A-Za-z/.?_=&0-9#]*)', re.I)
        lines = value_list[4]
        for i in xrange(len(lines)):
            line_entry = lines[i]
            test_url = grab_url.findall(line_entry)
            if remove_empty_lines != 0:
                if len(line_entry) != 1:
                    #print line_entry
                    subject_entry = ET.SubElement(subject_menu, "item", attrib = {"label" : line_entry})
                    subject_entry_action = ET.SubElement(subject_entry, "action", attrib = {"name": "Execute"})
                    subject_entry_execute = ET.SubElement(subject_entry_action, "command")
                    if test_url != []:
                        subject_entry_execute.text = "%s %s" % (browser, test_url[0][0])
                    else:
                        subject_entry_execute.text = "true"
                else:
                    pass
            else:
                subject_entry = ET.SubElement(subject_menu, "item", attrib = {"label" : line_entry})
                subject_entry_action = ET.SubElement(subject_entry, "action", attrib = {"name": "Execute"})
                subject_entry_execute = ET.SubElement(subject_entry_action, "command")
                if test_url != []:
                    subject_entry_execute.text = "%s %s" % (browser, test_url[0][0])
                else:
                    subject_entry_execute.text = "true"
        submenu_separator = ET.SubElement(menu, "separator")
        setread_entry = ET.SubElement(menu, "item", attrib = {"label":u"set read"})
        setread_entry_action = ET.SubElement(setread_entry, "action", attrib = {"name":"Execute"})
        setread_entry_execute = ET.SubElement(setread_entry_action, "command")
        setread_entry_execute.text = "%s --setread %s" % (sys.argv[0], mail_num)
        delete_menu = ET.SubElement(menu, "menu", attrib = {"id":str(mail_num) + "-delete-menu","label":u"delete"})
        delete_entry = ET.SubElement(delete_menu, "item", attrib = {"label":u"confirm"})
        delete_entry_action = ET.SubElement(delete_entry, "action", attrib = {"name":"Execute"})
        delete_entry_execute = ET.SubElement(delete_entry_action, "command")
        delete_entry_execute.text = "%s --delete %s" % (sys.argv[0], mail_num)


    def __pipeMenu(self, data_dict, state):
        """ output pipe menu xml structure """
        root = ET.Element("openbox_pipe_menu")
        if len(data_dict) == 0:
            empty_entry = ET.SubElement(root, "item", attrib = {"label":"no new mails"})
            empty_entry_action = ET.SubElement(empty_entry, "action", attrib = {"name":"Execute"})
            empty_entry_execute = ET.SubElement(empty_entry_action, "command")
            empty_entry_execute.text = "true"
        else:
            for i in data_dict.keys():
                if data_dict[i][3] != "deleted" and data_dict[i][3] != "seen":
                    self.__xmlSegment(root, i, data_dict.get(i))
        separator = ET.SubElement(root, "separator")

        refresh_entry = ET.SubElement(root, "item", attrib = {"label":u"refresh"})
        refresh_entry_action = ET.SubElement(refresh_entry, "action", attrib = {"name":"Execute"})
        refresh_entry_execute = ET.SubElement(refresh_entry_action, "command")
        refresh_entry_execute.text = "%s --update" % (sys.argv[0])

        if osd_on != 0:
            if state == 0:
                state_entry = ET.SubElement(root, "item", attrib = {"label":"enable osd"})
                state_entry_action = ET.SubElement(state_entry, "action", attrib = {"name":"Execute"})
                state_entry_execute = ET.SubElement(state_entry_action, "command")
                state_entry_execute.text = "%s --osdtoggle" % (sys.argv[0])
            else:
                state_entry = ET.SubElement(root, "item", attrib = {"label":"disable osd"})
                state_entry_action = ET.SubElement(state_entry, "action", attrib = {"name":"Execute"})
                state_entry_execute = ET.SubElement(state_entry_action, "command")
                state_entry_execute.text = "%s --osdtoggle" % (sys.argv[0])

        open_entry = ET.SubElement(root, "item", attrib = {"label":u"open mails"})
        open_entry_action = ET.SubElement(open_entry, "action", attrib = {"name":"Execute"})
        open_entry_execute = ET.SubElement(open_entry_action, "command")
        open_entry_execute.text = '%s' % (mail_agent)

        xml_string = '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root)
        return xml_string


    def __onScreen(self, print_list):
        """ make use of pyosd """
        num_lines = len(print_list)
        try:
            osd = pyosd.osd(lines = num_lines, timeout = delay, align = alignment, pos = position, font = font, colour = colour, shadow = shadow)
            osd.set_vertical_offset(vertical_offset)
            osd.set_horizontal_offset(horizontal_offset)
            if shadow != 0:
                osd.set_shadow_colour(shadow_colour)
                osd.set_shadow_offset(shadow_offset)
            if just_text != 0:
                osd.display(text)
            else:
                if layout == 1:
                    """ show: > [date] :: [from] :: [subject] < """
                    [osd.display("> " + print_list[i][0] + " :: " + print_list[i][1] + " :: " + print_list[i][2] + " <", line = i) for i in xrange(num_lines)]
                elif layout == 2:
                    """ show: > [from] :: [subject] < """
                    [osd.display("> " + print_list[i][1] + " :: " + print_list[i][2] + " <", line = i) for i in xrange(num_lines)]
                elif layout == 3:
                    """ show: > [date] :: [from] < """
                    [osd.display("> " + print_list[i][0] + " :: " + print_list[i][1] + " <", line = i) for i in xrange(num_lines)]
                elif layout == 4:
                    """ show: > [from] < """
                    [osd.display("> " + print_list[i][1] + " <", line = i) for i in xrange(num_lines)]
            osd.wait_until_no_display()
        except:
            pass


    def processing(self):
        """ sends data from temp_file to server and gets data from server """
        f = shelve.open(self.tmp_file, 'c')
        os.chmod(self.tmp_file, 0600)
        ## read stuff from tmp_file
        try:
            mail_dict = f['mail_dict']
        except KeyError:
            mail_dict = dict()
        try:
            state = f['state']
        except KeyError:
            state = 1

        ##  write mailstuff to tmp_file
        mail_dict = self.__imapConnect(mail_dict)
        f['mail_dict'] = mail_dict
        f['state'] = state
        xml_str = self.__pipeMenu(mail_dict, state)
        f['xml_str'] = xml_str
        f.close()

        ##  print to display 
        if osd_on != 0 and state != 0 and len(mail_dict.values()) != 0:
            self.__onScreen(mail_dict.values())


    def delete(self, mail_num):
        """ append deleted flag to mail list according to number """
        f = shelve.open(self.tmp_file, 'w')

        mail_dict = f['mail_dict']
        state = f['state']
        mail_dict[int(mail_num)][3] = 'deleted'
        xml_str = self.__pipeMenu(mail_dict, state)
        f['xml_str'] = xml_str

        f['mail_dict'] = mail_dict
        f.close()


    def setread(self, mail_num):
        """ append seen flag to mail list according to number """
        f = shelve.open(self.tmp_file, 'w')

        mail_dict = f['mail_dict']
        state = f['state']
        mail_dict[int(mail_num)][3] = 'seen'
        xml_str = self.__pipeMenu(mail_dict, state)
        f['xml_str'] = xml_str

        f['mail_dict'] = mail_dict
        f.close()


    def osdToggle(self):
        """ toggle osd mail notifying on or off - sometimes annoying """
        f = shelve.open(self.tmp_file, 'w')

        try:
            mail_dict = f['mail_dict']
        except KeyError:
            mail_dict = dict()
        try:
            state = f['state']
        except KeyError:
            state = 1
        if state == 0:
            state = 1
        else:
            state = 0

        xml_str = self.__pipeMenu(mail_dict, state)
        f['xml_str'] = xml_str
        f['state'] = state

        f.close()


    def printXml(self):
        f = shelve.open(self.tmp_file)
        try:
            xml_output = f['xml_str']
        except KeyError:
            mail_dict = dict()
            state = 1
            xml_output = self.__pipeMenu(mail_dict, state)
        f.close()
        print xml_output


#-------------------------------------------------------------------------------             
#                                    Main
#-------------------------------------------------------------------------------             
import imaplib
import shelve, os, sys, re
import xml.etree.ElementTree as ET
try:
    import pyosd
except ImportError:
    pass

#-------------------------#
if __name__ == "__main__" :
#-------------------------#
    try:
        home = os.environ['HOME']
        os.access("%s/.checkmailrc" % home, os.F_OK|os.R_OK)
        src = "%s/.checkmailrc" % home
        execfile(src)
        del home, src
    except StandardError, e:
        sys.stderr.write("Please copy the checkmailrc file to ~/.checkmailrc and edit it according to your settings.\n\n")
        sys.stderr.write(str(e) + "\n\n")
        sys.exit()

    mails = Mails(server_name, user_name, user_password, user_mailbox)
    args = sys.argv[1:]
    if ('--delete' in args):
        mails.delete(sys.argv[2])
    elif ('--setread' in args):
        mails.setread(sys.argv[2])
    elif ('--update' in args):
        mails.processing()
    elif ('--osdtoggle' in args):
        mails.osdToggle()
    else:
        mails.printXml()
    del mails


# }}} ##  fold markers stop

# vim: set ft=python ts=4 sw=4 foldmethod=marker :

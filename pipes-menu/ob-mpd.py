#!/usr/bin/env python
#
# Author: John Eikenberry <jae@zhar.net>
# License: GPL 3.0 <http://www.gnu.org/licenses/gpl.txt>
#
# Changelog
# 2007-09-09 - Fixed compatibility issue with mpdclient2 version 1.0
#              vs. 11.1 which I have (debian).
# 2007-11-18 - Added playlist load/clear support.
# 2009-01-26 - Changed playlist load behaviour to clear/load/play in one go.
# 2009-06-30 - Changed order to work better with menu middle set
#
#
# This script depends on py-libmpdclient2 which you can get from 
# http://incise.org/index.cgi/py-libmpdclient2
#
# Usage:
# Put an entry in ~/.config/openbox/menu.xml:
# <menu id="mpd" label="MPD" execute="~/.config/openbox/scripts/ob-mpd.py" />
#
# Add the following wherever you'd like it to be displayed in your menu:
# <menu id="mpd" />
#
#
# Originally Based on code by John McKnight <jmcknight@gmail.com>
#
# Almost completely reworked, including:
# 
#              Changed to use libmpdclient2.
#              Refactored/Cleaned up the code.
#              Added random/repeat toggle indicators. 
#              Changed Pause/Play so only the appropriate one would show up.
#              Added actions to start and stop mpd daemon.
#              Added exception to deal with no id3 tags.
#              Added volume controls.
#              Added output setting controls.
#              Determine location of script dynamically instead of hardcoded

import os, sys, socket
import mpdclient2

argv = sys.argv

# The default port for MPD is 6600.  If for some reason you have MPD
# running on a different port, change this setting.
mpdPort = 6600

# Client program and args as list or tuple
CLIENT = 'x-terminal-emulator'
CLIENT_ARGS = ('-name', 'ncmpc', '-e', 'ncmpcpp')
#CLIENT_ARGS = ('-name', 'ncmpc', '-geometry', '80x10', '-e', 'ncmpc')

# determin path to this file
my_path = sys.modules[__name__].__file__
# if this fails for some reason, just set it manually.
# Eg.
# my_path = "~/.config/openbox/scripts/ob-mpd.py"


separator = "<separator />"
info = """<item label="%s" />"""
action = ("""<item label="%s"><action name="Execute">"""
        """<execute>MY_PATH %s</execute>"""
        """</action></item>""").replace("MY_PATH",my_path)
menu = """<menu id="%s" label="%s">"""
menu_end = """</menu>"""


try:
    server = mpdclient2.connect(port=mpdPort)
except socket.error:
    # If MPD is not running.
    if len(argv) > 1:
        arg = argv[1]
        if arg == 'start':
            os.system('mpd')
    else:
        print ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
              "<openbox_pipe_menu>")
        print action % ('MPD is not running  [start]','start')
        print "</openbox_pipe_menu>"

else: # part of server try block

    song = server.currentsong()
    stats = server.stats()
    status = server.status()

    if status['state'] == "stop":
        display_state = "Not playing"
    else:
        try:
            display_state = "%s - %s" % (song.artist, song.title)
        except (AttributeError, KeyError): # no id3 tags
            display_state = os.path.basename(song.file)
        if status['state'] == "pause":
            display_state += " (paused)"
    display_state = display_state.replace('"',"'")
    display_state = display_state.replace('&','&amp;')

    if len(argv) > 1:

        state = status.state
        def play():
            if state == "stop" or state == "pause":
                server.play()

        def pause():
            if state == "play":
                server.pause(1)
            elif state == "pause":
                server.play()

        def stop():
            if state == "play" or state == "pause":
                server.stop()

        def prev():
            if state == "play":
                server.previous()

        def next():
            if state == "play":
                server.next()

        random_state = int(status.random)
        def random():
            if random_state:
                server.random(0)
            else:
                server.random(1)

        repeat_state = int(status.repeat)
        def repeat():
            if repeat_state:
                server.repeat(0)
            else:
                server.repeat(1)

        def kill():
            try:
                server.kill()
            except EOFError:
                pass

        def update():
            server.update()

        def volume(setto):
            relative = (setto[0] in ['+','-'])
            setto = int(setto)
            if relative:
                newvol = int(status.volume) + setto
                newvol = newvol <= 100 or 100
                newvol = newvol >= 0 or 0
            server.setvol(setto)

        def client():
            os.execlp(CLIENT, CLIENT, *CLIENT_ARGS)

        def enable(output_id):
            server.enableoutput(int(output_id))

        def disable(output_id):
            server.disableoutput(int(output_id))

        def load(list_name):
            server.clear()
            server.load(list_name)
            server.play()

        def clear():
            server.clear()

        if   (argv[1]     == "play"):    play()
        elif (argv[1]     == "pause"):   pause()
        elif (argv[1]     == "stop"):    stop()
        elif (argv[1][:4] == "prev"):    prev()
        elif (argv[1]     == "next"):    next()
        elif (argv[1]     == "random"):  random()
        elif (argv[1]     == "repeat"):  repeat()
        elif (argv[1]     == "volume"):  volume(argv[2])
        elif (argv[1]     == "client"):  client()
        elif (argv[1]     == "kill"):    kill()
        elif (argv[1]     == "update"):  update()
        elif (argv[1]     == "enable"):  enable(argv[2])
        elif (argv[1]     == "disable"): disable(argv[2])
        elif (argv[1]     == "load"):    load(argv[2])
        elif (argv[1]     == "clear"):   clear()

    else:
        # 
        print """<?xml version="1.0" encoding="UTF-8"?>"""
        print """<openbox_pipe_menu>"""
        print action % (display_state,'client')
        print separator
        print menu % ("volume","Volume: %s%%" % status.volume)
        print action % ('[100%]','volume 100')
        print action % (' [80%]','volume 80')
        print action % (' [60%]','volume 60')
        print action % (' [40%]','volume 40')
        print action % (' [20%]','volume 20')
        print action % ('[Mute]','volume 0')
        print menu_end
        print menu % ("playlist","Playlist")
        print action % ('clear','clear')
        print separator
        for entity in server.lsinfo():
            if 'playlist' in entity:
                playlist = entity['playlist']
                print action % (playlist, 'load %s' % playlist)
        print menu_end
        print menu % ("output","Audio Output")
        for out in server.outputs():
            name,oid = out['outputname'],out['outputid']
            on = int(out['outputenabled'])
            print action % ("%s [%s]" % (name, on and 'enabled' or 'disabled'),
                "%s %s" % ((on and 'disable' or 'enable'), oid))
        print menu_end
        print separator
        print action % ('Previous','prev')
        print action % ('Next','next')
        if status['state'] in ["pause","stop"]:
            print action % ('Play','play')
        if status['state'] == "play":
            print action % ('Pause','pause')
        print action % ('Stop','stop')
        print separator
        print action % ('Toggle random %s' % (
            int(status.random) and '[On]' or '[Off]'), 'random')
        print action % ('Toggle repeat %s' % (
            int(status.repeat) and '[On]' or '[Off]'), 'repeat')
        print separator
        print action % ('Update Database','update')
        print action % ('Kill MPD','kill')
        print "</openbox_pipe_menu>"

#        print menu % ("Song Info","Volume: %s%%" % status.volume)
#        print info % ('%s kbs' % status.bitrate)
#        print separator
#        print info % ("Artists in DB: %s" % stats.artists)
#        print info % ("Albums in DB: %s" % stats.albums)
#        print info % ("Songs in DB: %s" % stats.songs)


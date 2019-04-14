#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (c) 2012 Eli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#===============================================================================
#Openbox menu writers

def marker(isMarked):
    if isMarked is None:
        return ""
    if isMarked:
        return "=> "
    else:
        return ".     "

class Label():
    def __init__(self, label, isMarked=None):
        self.label = label
        self.isMarked = isMarked
    
    def write(self):
        formattedLabel = quoteattr(marker(self.isMarked) + self.label)
        
        print("<item label={0}>".format(formattedLabel))
        print("</item>")

class Button():
    def __init__(self, label, commands, isMarked=None):
        self.label = label
        self.commands = commands
        self.isMarked = isMarked
    
    def write(self):
        formattedLabel = marker(self.isMarked) + self.label
        formattedLabel = quoteattr(formattedLabel)
        
        command = createCommand(self.commands)
        
        print("<item label={0}>".format(formattedLabel))
        print(" <action name=\"Execute\">")
        print("  <execute>{0}</execute>".format(command))
        print(" </action>")
        print("</item>")

class Menu():
    def __init__(self, id, label, entries=None, isMarked=None):
        self.id = id
        self.label = label
        self.entries = entries
        self.isMarked = isMarked
        
    def write(self):
        formattedMarker = marker(self.isMarked) + self.label
        print("<menu id={0} label={1}>".format(quoteattr(self.id),
                                               quoteattr(formattedMarker)))
        
        for entry in self.entries:
            if entry is not None:
                entry.write()

        print("</menu>")

class PipeMenu():
    def __init__(self, label, commands, isMarked=None):
        self.label = label
        self.commands = commands
        self.isMarked = isMarked
    
    def write(self):
        formattedLabel = quoteattr(marker(self.isMarked) + self.label)

        command = createCommand(self.commands)

        print("<menu execute={0} id={1} label={2}/>".format(quoteattr(command),
                                                            quoteattr(command),
                                                            formattedLabel))

class Separator():
    def __init__(self, label=None):
        self.label = label
    
    def write(self):
        if self.label is None:
            print("<separator/>")
        else:
            print("<separator label={0}/>".format(quoteattr(self.label)))

class Container():
    def __init__(self, entries):
        self.entries = entries
        
    def write(self):
        print("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        print("<openbox_pipe_menu>")

        if isinstance(self.entries, list):
            for entry in self.entries:
                if entry is not None:
                    entry.write()
        else:
            self.entries.write()

        print("</openbox_pipe_menu>")

#===============================================================================
#Imports

import os
import sys

from pipes import quote

from urllib import unquote_plus
from xml.sax.saxutils import escape, unescape, quoteattr

import ConfigParser

try:
    import Tkinter
    import tkSimpleDialog

    import xmmsclient
    from xmmsclient import collections as xc
except ImportError as error:
    Container([Separator("Failed to load required modules!"), Separator(str(error)) ]).write()
    sys.exit(1)

#===============================================================================
#Helper Methods    
def createCommand(parameters):   
    return __file__ + ' ' + ' '.join([quoteattr(str(i)) for i in parameters])

def humanReadableSize(size):
    for x in ['bytes','KB','MB','GB']:
        if size < 1024.0:
            return "%3.2f%s" % (size, x)
        size /= 1024.0
        
def humanReadableDuration(milliseconds):
    seconds = int(milliseconds) / 1000
    minutes, seconds = divmod(seconds, 60)
    if minutes > 0:
        return "{0}m {1}s".format(minutes, seconds)
    else:
        return "{1}s".format(seconds)

def readString(dictionary, key, default=""):
    if key in dictionary:
        value = dictionary[key]
        if isinstance(value, basestring):
            return value.encode('utf8')
        else:
            return str(value)
    else:
        return default



#===============================================================================
#Writers
class AlphabetIndex():
    def write(self):
        indexKeys = map(chr, range(65, 91))
        for key in indexKeys:
            artist = xc.Match( field="artist", value= str(key)+"*" )          
            results = xmms.coll_query_infos( artist, ["artist"])
            
            groupLabel = "{0} ({1})".format(str(key), str(len(results)))
            PipeMenu(groupLabel, ["alphabetIndexArtists", str(key)] ).write()

class ArtistsList():
    def __init__(self, artist):
        self.artistMatch = xc.Match( field="artist", value= str(artist)+"*" )          
            
    def write(self):   
        results = xmms.coll_query_infos(self.artistMatch, ["artist"] )

        for result in results:
            artist = readString(result, 'artist')
            PipeMenu(artist, ["indexAlbum", artist] ).write()

class AlbumList():
    def __init__(self, artist):
        self.artist = artist
        self.artistMatch = xc.Match(field="artist", value=artist)      

    def write(self):          
        results = xmms.coll_query_infos(self.artistMatch, ["date", "album"] )

        for result in results:
            if result["album"] is not None:
                album = readString(result, 'album')
                label = "[" + readString(result, 'date') + "] " + album
                PipeMenu(label, ["indexTracks", self.artist, album] ).write()

class TrackList():
    def __init__(self, artist, album):
        self.artist = artist
        self.album = album
        
        self.match = xc.Intersection(xc.Match(field="artist", value=self.artist), 
                                     xc.Match(field="album", value=self.album))
    
    def write(self):
        results = xmms.coll_query_infos( self.match, ["tracknr", "title", "id"])

        counter = 0
        for result in results:
            id = str(result["id"])
            title = readString(result, 'title')
            trackNumber = readString(result, 'tracknr')
            
            addToCurrentPlaylist = Button("Add to Playlist", ["track", "add", str(id)] )
            trackInfo = PipeMenu("Infos", ["track", "info", str(id)] )  
            
            Menu("xmms-track-"+id, trackNumber + " - " + title, [addToCurrentPlaylist, trackInfo]).write()
            counter +=1

        Separator().write()
        Button("Add to Playlist", ["album", "add", self.artist, self.album] ).write()

class TrackInfo():
    def __init__(self, id):
        self.id = int(id)
                                     
    def write(self):
        minfo = xmms.medialib_get_info(self.id)

        Label("Artist \t: " + readString(minfo, 'artist')).write()
        Label("Album \t: " + readString(minfo, 'album')).write()
        Label("Title \t: " + readString(minfo, 'title')).write()
        Label("Duration \t: " + humanReadableDuration(minfo['duration'])).write()
        Separator().write()     
        Label("Size \t\t: " + humanReadableSize(minfo["size"])).write()
        Label("Bitrate \t: " + readString(minfo, 'bitrate')).write()
        
        url = unquote_plus(readString(minfo, 'url'))
        filename = url.split('/')[-1]

        Label("Url \t: " + url).write()
        Label("File \t: " + filename).write()

class ConfigMenu():
    def write(self):
        Separator("Presets:").write()
        ConfigPresets().write()
        Separator().write()
        ConfigView().write()

class ConfigPresets():
    def __init__(self):
        xmmsDirectory = xmmsclient.userconfdir_get()
        configPath = os.path.join(xmmsDirectory, "clients/openboxMenu/configPresets.ini")
    
        self.errorMessage = None
    
        self.config = ConfigParser.RawConfigParser()
        try:
            result = self.config.read(configPath)
            if len(result) != 1:
                self.errorMessage = 'Preset file not found'
        except ConfigParser.ParsingError as error:
            self.errorMessage = 'Preset file parsing error'
        
    def load(self, name):    
        for key, value in self.config.items(name):
            xmms.config_set_value(key, value)
        
    def write(self):
        if self.errorMessage != None:
            Separator(self.errorMessage).write()
            return
        
        for preset in self.config.sections():
            isActive = True
            
            for key, value in self.config.items(preset):
                actualValue = xmms.config_get_value(key)
                if value != actualValue:
                    isActive = False
                    break
            
            Button(preset, ["preset-load", preset], isActive).write()
        
class ConfigView():
    def __init__(self, configKey = None):
        self.configKey = configKey

    def write(self):      
        resultData = xmms.config_list_values();
        
        if self.configKey is None:
            namespaces = set()
            submenues = list()
        
            for entry in resultData:
                namespaces.add(entry.split('.')[0])
                
            for setEntry in namespaces:
                submenues.append(PipeMenu(setEntry, ["menu", "config-view", str(setEntry)] ))
            
            Menu("view all", "configView", submenues).write()
             
        else:
            namespaces = list()
            for entry in resultData:
                if entry.startswith(self.configKey):
                    namespaces.append(entry)
                    
            namespaces.sort()
            
            displayKeyChars = 0
            for entry in namespaces:
                displayKeyChars = max(displayKeyChars, len(entry))
                print(len(entry))
                                
            print(displayKeyChars)
            
            for entry in namespaces:
                padding = displayKeyChars - len(entry) + 1
                Label(entry + (" " * padding) + "\t" + resultData[entry]).write()
                
class VolumeMenu():
    def write(self):
        if xmms.playback_status() == xmmsclient.PLAYBACK_STATUS_STOP:
            Separator("Cannot set Volume on Stopped stream.").write()
            return
        
        currentVolumes = xmms.playback_volume_get()
        masterVolume = currentVolumes['master']

        volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
          
        volumeHasBeenSelected = False
        
        for id, val in enumerate(volumes):
            isSelectedVolume = False
        
            if masterVolume <= val and not volumeHasBeenSelected:
                isSelectedVolume = True
                volumeHasBeenSelected = True

            Button(str(val)+"%", ["volume", val], isSelectedVolume).write()

class PlaylistMenu():
    def write(self):
        playlists = xmms.playlist_list()
        activePlaylist = xmms.playlist_current_active()

        playlistMenu = list()
        playlistMenu.append(Button("New Playlist", ["createPlaylist"] ))
        playlistMenu.append(Separator())
        
        for playlist in playlists:
            if playlist.startswith('_'):
                continue
            
            loadButton = Button("load", ["loadPlaylist", playlist] )
            deleteButton = Button("delete", ["removePlaylist", playlist] )
            
            playlistMenu.append(Menu("xmms-playlist-"+playlist, playlist, [loadButton, Separator(), deleteButton], playlist == activePlaylist))

        Menu("xmms-playlists", "Playlist: {0}".format(activePlaylist), playlistMenu).write()
        Separator().write()
        
        displayRange = 10

        activeId = xmms.playback_current_id()
        activePlaylistIds = xmms.playlist_list_entries()
        
        if (activePlaylistIds != None) and (activePlaylistIds.count(activeId) == 1):
            selectedIndex = activePlaylistIds.index(activeId)
            PlaylistEntriesMenu(selectedIndex, "both", displayRange).write()
        else:
            PlaylistEntriesMenu(0, "top", displayRange).write()

class PlaylistEntriesMenu():
    def __init__(self, pos, expandDirection, maxDisplayed = 50):
        self.entryIds = xmms.playlist_list_entries()
        if self.entryIds is None:
            return
        
        self.expandBottom = False
        self.expandTop = False
        
        if expandDirection == "bottom":
            if pos - maxDisplayed > 0:
                self.expandBottom = True
                
            self.positions = range(max(pos - maxDisplayed, 0), pos)
             
        if expandDirection == "top":
            if pos + maxDisplayed < len(self.entryIds):
                self.expandTop = True
                
            self.positions = range(pos, min(pos + maxDisplayed, len(self.entryIds)))
            
        if expandDirection == "both":
            halfDisplayed = maxDisplayed/2
            
            if pos - halfDisplayed > 0:
                self.expandBottom = True
            
            if pos + halfDisplayed < len(self.entryIds):
                self.expandTop = True
                
            self.positions = range(max(pos - halfDisplayed, 0), min(pos + halfDisplayed, len(self.entryIds)))
                
    def write(self):
        if self.entryIds is None:
            Label('Playlist is Empty').write()
            return
            
        if self.expandBottom:
            PipeMenu("... before", ["menu", "playlist-entries", str(self.positions[0]), "bottom"] ).write()
            
        try:
            currentPosition = xmms.playlist_current_pos()
        except:
            currentPosition = None

        for id in self.positions:		
            activeId = xmms.playback_current_id()
            
            medialibId = self.entryIds[id]

            result = xmms.medialib_get_info(medialibId)

            artist = readString(result, 'artist')
            album = readString(result, 'album')
            title = readString(result, 'title')

            subMenuId = "xmms-activePlaylist-" + str(medialibId)
            entryLabel = "{0}|  {1} - {2} - {3}".format(
                            str(id).zfill(3), artist, album, title)
            
            moveMenu = Menu("xmms-move-" + str(medialibId), "move",
                [
                    Button("move first", ["playlist-entry", "move", str(id), str(0)] ),
                    Button("move -5", ["playlist-entry", "move", str(id), str(id - 5)] ),
                    Button("move -1", ["playlist-entry", "move", str(id), str(id - 1)] ),
                    Button("move +1", ["playlist-entry", "move", str(id), str(id + 1)] ),
                    Button("move +5", ["playlist-entry", "move", str(id), str(id + 5)] ),
                    Button("move last", ["playlist-entry", "move", str(id), str(len(self.entryIds) - 1)] )
                ])
                         
            subMenu = Menu(subMenuId, entryLabel,
                [
                    Button("jump", ["jump", str(id)] ),
                    Separator(),
                    moveMenu,
                    Separator(),
                    PipeMenu("Infos", ["track", "info", str(medialibId)] ),
                    Separator(),
                    Button("delete", ["playlist-entry", "remove", str(id)] )
                ],
                medialibId == activeId ).write()
                
        if self.expandTop:
            PipeMenu("... after", ["menu", "playlist-entries", str(self.positions[-1]+1), "top"]).write()
        

#===============================================================================
#Main Menu
class MainMenu():
    def write(self):
        if xmms.playback_status() == xmmsclient.PLAYBACK_STATUS_PLAY:
            Button("⧐ Pause", ["pause"] ).write()
        else:
            Button("⧐ Play", ["play"] ).write()

        Button("≫ next", ["next"] ).write()
        Button("≪ prev", ["prev"] ).write()
        Separator().write()
        
        PipeMenu("Volume", ["menu", "volume"] ).write()
        Separator().write()
        
        PipeMenu("Medialib", ["menu", "index-alphabet"] ).write()
        PipeMenu("Config", ["menu", "config"] ).write()
        Separator().write()
        
        PlaylistMenu().write()

#===============================================================================
#Commands
def createPlaylist():
    root = Tkinter.Tk()
    root.withdraw()

    name = tkSimpleDialog.askstring("New Playlist Name",
                                    "Enter a new Playlist Name")
    if name is not None:
        xmms.playlist_create(name)

#===============================================================================
#Main
if __name__ == "__main__":
    xmms = xmmsclient.XMMSSync("xmms2-OpenboxMenu")
    try:
        xmms.connect(os.getenv("XMMS_PATH"))
        
    except IOError as detail:
        Container(Separator("Connection failed: "+ str(detail))).write()
        sys.exit(1)
    
    paramterCount = len(sys.argv)
    
    if paramterCount == 1:
        Container(MainMenu()).write()
    elif paramterCount >= 2:
        command = sys.argv[1]
        
        if command == "menu":
            menuName = str(sys.argv[2])
            
            if menuName == "playlist-entries":
                pos = int(sys.argv[3])
                direction = str(sys.argv[4])
                
                Container(PlaylistEntriesMenu(pos, direction)).write()
                
            if menuName == "volume":
                Container(VolumeMenu()).write()
            
            if menuName == "config":
                Container(ConfigMenu()).write()
            
            if menuName == "config-view":
                configKey = None
                if paramterCount == 4:
                    configKey = str(sys.argv[3])
                
                Container(ConfigView(configKey)).write()
                
            if menuName == "index-alphabet":
                Container(AlphabetIndex()).write()
            
        if command == "play":
            xmms.playback_start()
        
        if command == "pause":
            xmms.playback_pause()
            
        if command == "next":
            xmms.playlist_set_next_rel(1)
            xmms.playback_tickle()
            
        if command == "prev":
            xmms.playlist_set_next_rel(-1)
            xmms.playback_tickle()
  
        if command == "jump":
            position = int(sys.argv[2])
            xmms.playlist_set_next(position)
            xmms.playback_tickle()
        
        if command == "track":
            trackCommand = str(sys.argv[2])
            trackId = int(sys.argv[3])
            
            if trackCommand == "add":
                xmms.playlist_insert_id(0, trackId)
                
            if trackCommand == "info":
                Container(TrackInfo(trackId)).write()

        if command == "album":
            albumCommand = str(sys.argv[2])
            artistName = str(sys.argv[3])
            albumName = str(sys.argv[4])

            if albumCommand == "add":
                match = xc.Intersection(xc.Match(field="artist", value=artistName),
                                        xc.Match(field="album", value=albumName))

                trackIds = xmms.coll_query_infos( match, ["id"])
                for trackId in trackIds:
                    xmms.playlist_add_id(trackId["id"])
            
        if command == "playlist-entry":
            subCommand = str(sys.argv[2])
            entryIndex = int(sys.argv[3])
            
            if subCommand == "move":
                newIndex = int(sys.argv[4])
                xmms.playlist_move(entryIndex, newIndex)
            
            if subCommand == "remove":
                xmms.playlist_remove_entry(entryIndex)
        
        if command == "createPlaylist":
            createPlaylist()
        
        if command == "loadPlaylist":
            playlistName = str(sys.argv[2])
            xmms.playlist_load(playlistName)
            
        if command == "removePlaylist":
            playlistName = str(sys.argv[2])
            xmms.playlist_remove(playlistName)
            
        if command == "preset-load":
            presetName = str(sys.argv[2])
            ConfigPresets().load(presetName)
            
        if command == "volume":
            volume = int(sys.argv[2])
            xmms.playback_volume_set("master", volume)
          
        if command == "alphabetIndexArtists":
            index = str(sys.argv[2])
            Container(ArtistsList(unescape(index))).write()
            
        if command == "indexAlbum":
            artist = str(sys.argv[2])
            Container(AlbumList(unescape(artist))).write()
        
        if command == "indexTracks":
            artist = str(sys.argv[2])
            album = str(sys.argv[3])
            Container(TrackList(unescape(artist), unescape(album))).write()


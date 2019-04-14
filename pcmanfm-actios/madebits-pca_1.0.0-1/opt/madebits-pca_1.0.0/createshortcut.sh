#!/bin/bash

# %f %w
file=$1
fileName=$2
desktopDir=${XDG_DESKTOP_DIR:-$HOME/Desktop}
desktopFileName="${desktopDir}/${fileName}.desktop"
if [ ! -f "$desktopFileName" ]; then
	echo -e "[Desktop Entry]\nVersion=1.0\nName=${fileName}\nExec=${file}\nTerminal=false\nType=Application\n" > "${desktopFileName}"
	lxshortcut -i ${desktopFileName}
else
	 zenity --error --text="File exists ${desktopFileName}"
fi

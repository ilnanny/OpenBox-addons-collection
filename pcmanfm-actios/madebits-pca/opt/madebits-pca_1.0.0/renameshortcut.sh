#!/bin/bash

newName=$(zenity --width 480 --height 160 --entry --title="Rename File"  --text="Please enter a new name:" --entry-text "$2")
if [[ -n "$newName" && ( "$newName" != "$2" ) ]]; then
	cd "$1" && mv "$2" "$newName"
	res=$?
	if [[ $res != 0 ]] ; then
    		zenity --error --text="Failed in $1 to rename $2 => $newName"
	fi
fi

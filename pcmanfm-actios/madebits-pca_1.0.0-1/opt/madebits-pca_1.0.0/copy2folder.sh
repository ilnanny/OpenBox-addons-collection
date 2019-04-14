#!/bin/bash

folder=$(zenity --file-selection --directory --title="Copy To Folder")
if [[ $folder ]]; then
	# cp -r $@ "$folder"
	for var in "$@"
	do
	    cp -r "$var" "$folder"
	done
fi


#!/bin/bash

STEAMAPPS=~/.steam/steam/steamapps/ 
ICONS=~/.local/share/icons/hicolor/32x32/apps/ 


for file in "$STEAMAPPS"/*.acf; do 
    ID=$(grep -w -m 1 '"appid"' "$file" | sed -r 's/[^"]*"appid"[^"]*"([^"]*)"/\1/') 
    NAME=$(grep -w -m 1 '"name"' "$file" | sed -r 's/[^"]*"name"[^"]*"([^"]*)"/\1/') 
if [ ! -s $ICONS/steam_icon_$ID.png ]; then 
	echo "$NAME's icon is missing, retrieving from web"
	ICONHASH=$(steamcmd  +app_info_print $ID +exit | grep -w -m 1 "icon" | sed -r 's/[^"]*"icon"[^"]*"([^"]*)"/\1/');
	wget http://media.steampowered.com/steamcommunity/public/images/apps/$ID/$ICONHASH.jpg -O "$ICONS"steam_icon_$ID.png
else
	echo "$NAME's icon is present, skipping"
fi
done
	echo "done"

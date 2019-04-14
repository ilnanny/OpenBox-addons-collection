#!/bin/bash

/bin/cp "$1" "$1.$(date +%Y%m%d-%H%M%S).bak"

res=$?
if [[ $res != 0 ]] ; then
    zenity --error --text="Failed $1 (not root?)"
fi

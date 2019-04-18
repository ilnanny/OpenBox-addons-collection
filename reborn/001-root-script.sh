#!/bin/bash
set -e
#
##########################################################
# Author 	: 	Palanthis (palanthis@gmail.com)
# Website 	: 	http://github.com/Palanthis
# License	:	Distributed under the terms of GNU GPL v3
# Warning	:	These scripts come with NO WARRANTY!!!!!!
##########################################################

echo "###################################"
echo "#### This must be run as root  ####"
echo "####   using su, NOT sudo     #####"
echo "###################################"

chown palanthis:users *

# Re-sync Repos
pacman -Syy

# Fix Enviornment
echo QT_QPA_PLATFORMTHEME=qt5ct >> /etc/environment

# Enable network time
systemctl enable systemd-networkd.service

systemctl start systemd-networkd.service

systemctl enable systemd-timesyncd.service

systemctl start systemd-timesyncd.service

timedatectl set-ntp true

hwclock --systohc --utc

echo " "
echo "Let's make sure everything looks right!"

timedatectl status

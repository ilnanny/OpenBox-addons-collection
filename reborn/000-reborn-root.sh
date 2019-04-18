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

# Fix sudoers (this will enable members of wheel to
# run any command under sudo without being prompted
# for a password) *REBORN ONLY!*
tar xzf tarballs/sudoers.tar.gz -C /tmp/ --overwrite
mv /etc/sudoers /etc/sudoers.bak
mv /tmp/sudoers /etc/sudoers
rm -rf /etc/sudoers.d

sudo pacman -Sy rebornos-keyring aurarchlinux-keyring --needed --noconfirm
sudo pacman-key --populate rebornos aurarchlinux

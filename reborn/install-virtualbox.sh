#!/bin/bash
set -e

#Install VirtualBox and optional components
sudo pacman -S virtualbox --noconfirm --needed
sudo pacman -S virtualbox-host-dkms --noconfirm --needed
sudo pacman -S virtualbox-guest-iso --noconfirm --needed
yaourt -S virtualbox-ext-oracle --noconfirm --needed

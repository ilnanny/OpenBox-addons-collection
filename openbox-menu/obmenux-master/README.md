# obmenux : the Openbox Menu Editor X version
an experimental version of obmenu Openbox menu editors

Features obmenux 1.3 has that obmenu 1.0 lacks:  
   + icon support (shows icons, allows setting icons, browse with preview)
   + helpful messages in case of any file errors, instead of crashing
   + edits separator labels  
   + moves items and menus in and out of menus (without rewriting them)
   + any arrangement of menus and their ids can be viewed and edited, even
     invalid arrangements that would hide menus and links from showing up, so
     that broken menus can be fixed, and menus with circular references won't
     crash the menu editor
   + Openbox 3.6 compatible for editing command tags
     (sorry, obmenux still has no support for action tags other than
     command or execute, such as tags that set startup notification and
     window locations)

The point of this fork was to add the additional feature of moving items and menus freely between menus, and maybe other features, and to combine that with bugfixes from other versions of obmenu, and more bugfixes. So this version will be available here for downloading as an alternative to downloading another obmenu version and applying patches manually each time a functioning version of obmenu is wanted when setting up a desktop that uses Openbox. (Openbox can be used as a desktop environment by itself or as the window manager for LXDE or Lubuntu.)

The folder obmenux-[version number] is a complete set of files and installer scripts for using the specified version. Other related and relevant files, such as this README will be outside that folder.

## about versions and forks of obmenu in general:

The original seems out-of-date, not having been changed significantly since it was written in 2005 to 2006, despite numerous patches by distros and forks of it suggesting changes. Changes to the Openbox standards have also made the original version incapable of editing some otherwise valid Openbox menus without rewriting them and destroying much of their valid contents.

There are several sources of patches of obmenu and versions of obmenu by others, such as:
- obmenu-1.0-2+nmu2 in the Debian and Ubuntu repositories
- obmenu2
- obmenu3 which is written in Pascal and compiled with its Pascal dependencies
- obmenu [untitled version] by GLolol, 2015

This current obmenux started with just copying files and editing them to see what would happen. So it doesn't have an automatic GitHub connection as a fork of any other version. As of 1.2.0 the code is nearly cleaned up and probably suitable for packaging.

This project uses precisely specified versions, since 1.1.24. Precise specification of versions in the installer folder and in the About dialog of an application is useful for knowing what version is installed, what to report issues against, and what to download and install for an improvement. (Version 1.1.1 of the installer folder had rolling commits to it in the master branch, without updating the version number shown. Testers found that practice caused uncertainty and inconvenience.)

Improvements are in the pipeline.

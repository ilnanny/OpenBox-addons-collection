Vera autostart plugin
=====================

This is the autostart plugin for the Vera Desktop Environment.

Its job is to properly parse every application in the common autostart
directories (e.g. /etc/xdg/autostart) and to start them at the appropriate phase.

How do I specify a phase?
-------------------------

To specify a phase, it's only necessary to put the key X-Vera-Autostart-Phase in the .desktop files.

If no phase is specified, the plugin will default to OTHER.

Phases are often not needed outside of vera. We use them to properly launch the WM, the Panel, and
other "high-priority" things.


Does this plugin also handle the restart of crashed applications?
-----------------------------------------------------------------

No (for now :P).


Building
--------

AutostartPlugin requires only libvera, gee-1.0 and libpeas-1.0.
To build and install, simply run

	bake
	sudo bake install

Put the compiled plugin and its .plugin file in /usr/share/vera/plugins, enable it and enjoy!

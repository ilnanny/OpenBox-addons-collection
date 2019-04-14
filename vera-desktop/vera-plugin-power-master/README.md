vera power plugin
=================

vera-plugin-power is the vera plugin that shows the informations of the currently
plugged batteries.

It uses UPower, so every device supported by it is also supported by this plugin.  
This includes some wireless mice and keyboards, as well as UPS and phones.

This plugin also handles the power-related settings in the user session (e.g
brightness).  
The global settings (handled directly by logind) will not be touched by vera-plugin-power.

Is vera-plugin-power a power manager?
-------------------------------------

No. Thus it doesn't conflict with other manager such as tlp or laptop-mode-tools.  

Semplice (7+) uses vera-plugin-power alongside tlp.

Building
--------

You need:

* valac (tested against vala 0.24)
* vera
* bake
* gcc
* gtk+-3.0
* upower-glib
* gio-2.0
* gee-1.0
* libpeas-1.0

To compile vera-plugin-power, just execute

	bake

You also need to install and compile the settings schemas.  
To do so, you can use the following:

	cd schemas
	sudo bake install
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

Installing
----------

Of course, you can install vera-plugin-power globally:

	sudo bake install # (from the top source directory)
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

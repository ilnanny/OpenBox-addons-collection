vera desktop plugin
===================

vera-plugin-desktop is the vera plugin that handles the desktop.

In the current iteration, it sets the wallpaper and it also provides
a nice application launcher.

Building
--------

You need:

* valac (tested against vala 0.24)
* vera
* bake
* gcc
* gtk+-3.0
* gio-2.0
* libpeas-1.0
* x11
* cairo

To compile vera-plugin-desktop, just execute

	bake

You also need to install and compile the settings schemas.  
To do so, you can use the following:

	cd schemas
	sudo bake install
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

Installing
----------

Of course, you can install vera-plugin-desktop globally:

	sudo bake install # (from the top source directory)
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

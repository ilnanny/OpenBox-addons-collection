vera openbox plugin
===================

vera-openbox-plugin is the plugin that handles communication between vera
and openbox.

Building
--------

You need:

* valac (tested against vala 0.24)
* vera
* bake
* gcc
* gio-2.0
* libpeas-1.0

To compile vera-plugin-openbox, just execute

	bake

You also need to install and compile the settings schemas.  
To do so, you can use the following:

	cd schemas
	sudo bake install
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

Installing
----------

Of course, you can install vera-plugin-openbox globally:

	sudo bake install # (from the top source directory)
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

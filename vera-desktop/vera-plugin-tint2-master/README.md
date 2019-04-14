Vera tint2 plugin
=================

vera-plugin-tint2 manages the tint2 panel in Vera.

Building
--------

You need:

* valac (tested against vala 0.24)
* vera
* bake
* gcc
* gio-2.0
* libpeas-1.0

To compile vera-plugin-tint2, just execute

	bake

You also need to install and compile the settings schemas.  
To do so, you can use the following:

	cd schemas
	sudo bake install
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

Installing
----------

Of course, you can install vera-plugin-tint2 globally:

	sudo bake install # (from the top source directory)
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas

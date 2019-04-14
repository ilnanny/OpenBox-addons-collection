obbrowser
=========

A very fast dynamic file browser that allows quick searching and launching of user directories and files.

![obbrowser](https://2.bp.blogspot.com/-JYbaONBw-1A/UN8O4Fog2UI/AAAAAAAAKYo/vr_XkJwfS78/s1600/obbrowser.png)

----

### Dependencies:

* [Gtk2](https://metacpan.org/pod/Gtk2)
* [Data::Dump](https://metacpan.org/pod/Data::Dump)
* [File::MimeInfo](https://metacpan.org/pod/File::MimeInfo)

### Set-up:

* To use this script with Openbox, insert the following
   line in your `menu.xml` file:

        <menu id="obbrowser" label="Disk" execute="obbrowser"/>

* If you're using it with [obmenu-generator](https://github.com/trizen/obmenu-generator), insert the following
   line in your `schema.pl` file:

        {pipe => ["obbrowser", "Disk", "drive-harddisk"]},

* Reconfigure openbox:

        openbox --reconfigure

* For low-level options, see the configuration file:

          ~/.config/obbrowser/config.pl

### Usage:
```
obbrowser [dir]
```

### Availability:

AUR: https://aur.archlinux.org/packages/obbrowser/

========
ob-randr
========

Creates an interactive pipe menu for the OpenBox window manager to allow users
easy access to xrandr information and actions.

.. image:: https://github.com/whiteinge/ob-randr/raw/master/ob-randr.png

Installation Instructions
=========================

1.  Download the script: https://github.com/whiteinge/ob-randr/raw/master/ob-randr.py
2.  Put it somewhere that makes sense::

        mv ob-randr.py $HOME/.config/openbox

3.  Make it executable::

        chmod 755 $HOME/.config/openbox/ob-randr.py

4.  Edit your ``$HOME/.config/openbox/menu.xml`` file and put this near the top
    inside ``<openbox_menu>``::

        <menu id="randr-menu" label="randr" execute="~/.config/openbox/ob-randr.py" />

5.  Add this inside the menu section that you want the menu to appear in::

        <menu id="randr-menu" />

Configuration File
==================

You can easily add custom commands to the menu by creating the file
``$HOME/.ob-randrrc``. The syntax looks like this::

    [Notebook]

    portrait: --output LVDS --primary --mode 1366x768 --output VGA-0 --mode 1440x900 --left-of LVDS --rotate left

    [Netbook]

    zoom out: --output LVDS --scale 1.3x1.3
    zoom in: --output LVDS --panning 1280x1024

The idea is that you can create machine-specific shortcuts. For example, with
my laptop at home I frequently connect to an external widescreen display turned
sideways. On my netbook, I frequently 'zoom out' to a higher resolution in
scaled-out mode or 'zoom in' to a higher resolution in panning mode.

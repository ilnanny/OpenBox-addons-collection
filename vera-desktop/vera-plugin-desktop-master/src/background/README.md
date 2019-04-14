Handling the background
=======================

There are some problems that we need to solve to get a reliable way to apply
backgrounds.  
We should keep in mind that:

 * We are still using X
 * X means that we may not have compositing active, so we need to enable
   the "fake transparency" for e.g. the panel and the terminal windows
 * This desktop plugin handles multiple monitors separately: there is a
   GtkWindow per monitor
 * Memory usage should be as low as possible

The fake transparency is achieved by putting the main XPixmap containing
the background in the _XROOTPMAP_ID Atom.  
This means that we are still linked to the X server and we can't be
independent.

The first step is to create an XPixmap of the size of the entire screen, and
the with it the relative cairo_xlibsurface_t.

As the pixmap contains the entire screen, only one is needed.

Cairo Subsurfaces are calculated for every monitor and they go to the
single desktop windows for painting.

Finally, the xpixmap should be put in the _XROOTPMAP_ID atom as said before.

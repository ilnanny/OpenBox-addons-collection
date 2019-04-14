vera-xsettings
==============

This is the reference implementation made by Owen Taylor of the XSETTINGS protocol,
coupled with a nice vapi binding so that it can be used with vala applications.

As this is the 'official' implementation of the protocol, why haven't you called it libxsettings?
-------------------------------------------------------------------------------------------------

A re-package of this reference implementation already exists, and it's in Debian too.

Unfortunately it doesn't contain the XSettingsManager object, which is what matters to us.
To avoid package conflicts, we called this library '(lib)vera-xsettings'.

I want to use this library from vala. Any pointers or, even better, examples?
-----------------------------------------------------------------------------

I'm too lazy to write a couple of examples, but it's used successfully in
[our own vera](https://github.com/vera-desktop/vera) (duh!).

By reading the (short) vapi you'll have a better idea.  
Currently the XSettings.Manager() object is not freed automatically, so you
need to call .destroy() when needed.


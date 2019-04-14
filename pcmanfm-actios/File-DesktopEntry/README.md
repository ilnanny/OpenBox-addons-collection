# File-DesktopEntry

You can use this module to work with `.desktop` files as specified
by the Freedesktop.org specification.

## INSTALLATION

If you are on Linux, the most convenient way to install this module is
via your package manager. On Debian or Ubuntu:

    sudo apt-get install libfile-desktopentry-perl

on Fedora, RHEL or CentOS:

    sudo yum install perl-File-DesktopEntry

note: on RHEL or CentOS you'd need to first install [EPEL](https://fedoraproject.org/wiki/EPEL):

    sudo yum install epel-release

If you can't install from a package manager, the best solution is installation using
your cpan client. This will take care of installing any dependencies:

    cpan File::DesktopEntry

To install this module manually, type the following:

    perl Makefile.PL
    make
    make test
    make install

## COPYRIGHT AND LICENCE

Copyright (c) 2005, 2007 Jaap G Karssenberg.
Maintained by Michiel Beijen.

All rights reserved.
This program is free software; you can redistribute it and/or
modify it under the same terms as Perl itself.

# Openbox Pipe Menus

Here are just a couple of the Openbox pipe menus that I use.

## obmail.pl

Display the sender and subject of any unread Gmails. Does not change the status
of these emails (i.e. they will remain unread). Also checks the local `~/mail`
folder for any new emails and displays these as well.

Requires the Perl IMAP client module from CPAN, as well as the Perl SSL socket
module to run correctly. Just edit the file to include your username and
password, and it should work fine. In theory, it could be used for any IMAP
email server, but I haven't tested this.



## obpacman.pl

Display all updates available for the pacman package manager. Information
displayed will include the currently installed version, as well as the new
version available.

Obviously, this requires pacman to work. Also, make a cronjob as root to update
the local databases periodically in order to prevent the need for root access on
this script.

## Help

See read [this](http://openbox.org/wiki/Help:Menus#Pipe_menus) to see how to use
these pipe menus.

Sorry for the poor documentation. Email any comments, complaints, concerns, etc.
to <velentr.rc@gmail.com>, or send me a message on Github.

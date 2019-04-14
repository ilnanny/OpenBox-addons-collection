#!/usr/bin/perl

use strict;

print "<openbox_pipe_menu>\n";

print "<separator label=\"Upgrades\" />\n";

my @pkgs = split(/\s/, `pacman -Qqu`);

if (@pkgs) {
    foreach my $pkg (@pkgs) {
        my $old = &getversion(`pacman -Qi $pkg`);
        my $new = &getversion(`pacman -Si $pkg`);

        print "<menu id=\"pkg-$pkg\" label=\"$pkg\">\n";
        print "  <item label=\"Old: $old\" />\n";
        print "  <item label=\"New: $new\" />\n";
        print "</menu>\n";
    }
} else {
    print "<item label=\"No upgrades available.\" />\n";
}

sub getversion {
    foreach (@_) {
        if (/^Version/) {
            my @fields = split /\s/;
            return pop @fields;
        }
    }
}

END {
    print "</openbox_pipe_menu>\n";
}

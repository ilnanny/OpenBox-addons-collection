#!/usr/bin/perl

# Author: Daniel "Trizen" Șuteu
# License: GPLv3
# Date: 18 July 2016
# Website: https://github.com/trizen

# A fast algorithm, based on powers of primes,
# for exactly computing very large factorials.

use 5.020;
use strict;
use warnings;

use Math::AnyNum qw(:overload);
use experimental qw(signatures);
use ntheory qw(forprimes todigits vecsum);

sub factorial_power ($n, $p) {
    ($n - vecsum(todigits($n, $p))) / ($p - 1);
}

sub factorial ($n) {

    my $f = 1;

    forprimes {
        $f *= $_**factorial_power($n, $_);
    } $n;

    return $f;
}

for my $n (0 .. 50) {
    say "$n! = ", factorial($n);
}

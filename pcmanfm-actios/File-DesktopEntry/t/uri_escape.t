use strict;
use warnings;
use Test::More;
use File::DesktopEntry;

use utf8;

plan skip_all => "Windows"
  if $^O eq 'MSWin32';

my $buffer = <<EOF;
[Desktop Entry]
Name=Foo!
Type=Application
EOF

my $entry = File::DesktopEntry->new_from_data($buffer);

# Test escaping reserved and unicode characters
$entry->set(Exec => q#/bin/foo %U#);

my @exec = $entry->parse_Exec("/home/#=& €");

is_deeply(\@exec,
    ['/bin/foo', 'file:///home/%23%3D%26%20%E2%82%AC'],
    "parse_Exec works with %U - special characters");

# Test unescaping characters
$entry->set(Exec => q#/bin/foo %F#);

@exec = $entry->parse_Exec("file:///home/#=& € €",
    'file:///home/%23%3D%26%20%E2%82%AC €');

is_deeply(\@exec,
    ['/bin/foo', "/home/#=& € €", "/home/#=& € €"],
    "parse_Exec works with %F - special characters");

done_testing;

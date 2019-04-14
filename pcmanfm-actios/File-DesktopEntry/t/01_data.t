use strict;
use warnings;
use Test::More tests => 25;

use_ok('File::DesktopEntry');
$File::DesktopEntry::_locale = ''; # reset locale for testing

my $file = File::Spec->catfile(qw/t applications foo.desktop/);
my $entry = File::DesktopEntry->new($file);
is($$entry{file}, $file, 'new(FILE) works');

$entry = File::DesktopEntry->new_from_file($file);
is($$entry{file}, $file, 'new_from_file(FILE) works');

ok(! $$entry{groups}, 'no premature hashing');

is( $entry->get('Comment'),
       	'The best viewer for Foo objects available!',
	'get() works');

is( $entry->get('Comment[eo]'), 'Tekstredaktilo',
	'get() works with locale string' );

is( $entry->get('Comment[ja]'),
	"\x{30c6}\x{30ad}\x{30b9}\x{30c8}\x{30a8}\x{30c7}\x{30a3}\x{30bf}",
	'get() works with locale in utf8' );

is( $entry->get('Desktop Action Edit', 'Name'),
	'Foo Viewer (edit image)',
	'get() works with alternative group' );

is( $entry->get_value('Comment'),
       	'The best viewer for Foo objects available!',
	'get_value() works' );

is( $entry->get_value('Name', 'Desktop Action Edit'),
	'Foo Viewer (edit image)',
	'get_value() works with alternative group' );

is( $entry->get('Foo'), undef, 'Non-existing key');
is( $entry->get('Foo', 'Foo'), undef, 'Non-existing group');

my $buffer = <<EOF;
[Desktop Entry]
Name=Foo!
Type=Application

[Bar]
# Group with Bar data
baz=true
;
EOF

$entry = File::DesktopEntry->new_from_data($buffer);
#use Data::Dumper; warn Dumper $entry;
is($entry->get('Name'), 'Foo!', 'new_from_data() works');
is(scalar(@{$$entry{groups}}), 2, 'number of groups correct');
is($entry->text, $buffer, 'text() works');

my $i = 0;
for (
	['C' => ''],
	['lang_COUNTRY.enc@MOD' =>
		'lang_COUNTRY@MOD|lang_COUNTRY|lang@MOD|lang'],
	['lang_COUNTRY.enc' => 'lang_COUNTRY|lang'],
	['lang@MOD'         => 'lang@MOD|lang'],
	['lang'             => 'lang']
) {
	++$i;
	is( File::DesktopEntry::_parse_lang($$_[0]), $$_[1],
		"language parsing $i");
}
$entry->set('Name[nl]' => 'dus ja');
is($entry->get('Name[nl_BE]'), 'dus ja', 'language parsing in get()');

$entry->set('Name[C]' => 'Something new');
is($entry->get('Name[POSIX]'), 'Something new', 'Aliases for default locale');

$ENV{XDG_DATA_HOME} = 't';
$file = File::Spec->catfile(qw/t applications bar baz.desktop/);
$$entry{name} = 'bar-baz';
is($entry->_data_home_file, $file, 'correct file name generated');
rmdir( File::Spec->catdir(qw/t applications bar/) ); # clean up


$file = File::Spec->catfile('t', 'applications', 'bar.desktop');
$entry = File::DesktopEntry->new;
$entry->set(Type => 'Application', Name => 'Bar');
$entry->set('Some Action', Run => 'bar');
$entry->write($file);

$entry = File::DesktopEntry->new($file);
is($entry->text,
"[Desktop Entry]
Version=1.0
Encoding=UTF-8
Type=Application
Name=Bar

[Some Action]
Run=bar
",
'write/read');

unlink($file); # clean up

my $text =
"[Desktop Entry]
Version=1.0
Encoding=UTF-8
# the field below gives the name
Name=Bar

Type=Application
";
$entry = File::DesktopEntry->new(\$text);
$entry->set(Name => 'MyBar');
$text =~ s/Bar/MyBar/;
is($entry->text, $text, 'comments are preserved');

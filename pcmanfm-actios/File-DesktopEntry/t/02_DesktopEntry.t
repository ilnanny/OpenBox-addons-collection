use strict;
use warnings;
use Test::More;

use File::DesktopEntry;
$File::DesktopEntry::_locale = ''; # reset locale for testing

my $file = File::Spec->catfile(qw/t applications foo.desktop/);

$ENV{XDG_DATA_HOME} = 't';
is(File::DesktopEntry->lookup('foo'), $file, 'lookup works 1');

# Constructor 1
{
	my $entry = File::DesktopEntry->new('foo');
	is($entry->get('Name'), 'Foo Viewer', 'new(NAME) works');
}

# Constructor 2
{
	my $entry = File::DesktopEntry->new(
		\"[Desktop Entry]\nName=dusss\nType=Link\n" );
	is($entry->get('Name'), 'dusss', 'new(\$TEXT) works');
}

# Info
{
	my $entry = File::DesktopEntry->new($file);
	is($entry->get('Name'), 'Foo Viewer', 'new(FILE) works');
	is($entry->Name, 'Foo Viewer', 'AUTOLOAD works');

	ok(! $entry->wants_uris, 'wants_uris()');
	ok($entry->wants_list, 'wants_list()');
}

# URI Parsing
{
	my @uris = (
		['file:///foo/bar', '/foo/bar'],
		['file:/foo/bar', '/foo/bar'],
		['file://localhost/foo/bar', '/foo/bar'],
		['file://foo/bar', 'smb://foo/bar'],
	);

	SKIP: {
		skip("Win32 specific uri parsing", 2) unless $^O eq 'MSWin32';
		push @uris,
			['file:///C:/foo', 'C:/foo'], # and not /C:/foo
			['file:////foo/bar', 'smb://foo/bar'] ;
	}

	my $i = 0;
	for (@uris) {
		is( (File::DesktopEntry::_paths($$_[0]))[0], $$_[1],
			"URI parsing ".++$i );
	}
}

# Check quoting rules
{
	my $entry = File::DesktopEntry->new($file);

	$entry->set(Exec => q#fooview " #);
	my $text = $$entry{groups}[ $entry->_group() ];
	ok( $text =~ /^Exec=fooview "\\\\""/m, "Exec escaping works 1");
		# Checks run-away quotes are handled

	$entry->set(Exec => q#fooview $foo '( )' '%f' \\#);
	$text = $$entry{groups}[ $entry->_group() ];
	ok( $text =~ /^Exec=fooview "\\\\\$foo" "\( \)" %f "\\\\\\\\"/m,
		"Exec escaping works 2");
		# Simple field codes do not need quotes
		# in fact, do get skipped if quoted.
		# \\ in regex is \ in text
		# \ in exec becomes \\ when quoting Exec key
		# \\ in any value becomes \\\\ in set()
		# \\\\ in text is matched by \\\\\\\\ in regex *sigh*

	my @exec = $entry->parse_Exec('bar');
	is_deeply(\@exec, ['fooview', '$foo', '( )', 'bar', '\\'],
		"Exec escaping works 3");

	$entry->set('Group Foo', Exec => 'exec $');
	is($entry->get('Group Foo', 'Exec'), 'exec $',
		'no quoting different group');
		# Exec should not be quoted here !
}

# Test %F
{
	my $entry = File::DesktopEntry->new($file);

	my $exec = $entry->parse_Exec();
	is($exec, q#fooview#, 'parse_Exec works without args');

	$exec = $entry->parse_Exec(qw#$bar baz file:///usr/share#);
	is($exec, q#fooview "\$bar" baz /usr/share#,
		'parse_Exec works with %F');

	my @exec = $entry->parse_Exec(qw#$bar baz file:///usr/share#);
	is_deeply(\@exec, ['fooview', '$bar', 'baz', '/usr/share'],
		'parse_Exec works with %F - list context');

	$entry->set(Exec => qw#fooview#);
	$exec = $entry->parse_Exec(qw/$bar baz/);
	is($exec, q#fooview "\$bar" baz#, 'parse_Exec defaults to %F');
}

# Test %U
if ( $^O ne 'MSWin32' ) {
	my $entry = File::DesktopEntry->new($file);
	$entry->set(Exec => q#fooview %%foo %U#);

	my $exec = $entry->parse_Exec('/usr/share', 'http://cpan.org');
	is($exec, q#fooview %foo file:///usr/share http://cpan.org#,
		"parse_Exec works with %U");

	my @exec = $entry->parse_Exec('/usr/share', 'http://cpan.org');
	is_deeply(\@exec,
		['fooview', '%foo', 'file:///usr/share', 'http://cpan.org'],
		"parse_Exec works with %U - list context");
}
# on Windows paths are different - lame fix for tests
else {
	my $entry = File::DesktopEntry->new($file);
	$entry->set(Exec => q#fooview %%foo %U#);

	my $exec = $entry->parse_Exec('C:/usr/share', 'http://cpan.org');
	is($exec, q#fooview %foo file:///C:/usr/share http://cpan.org#,
		"parse_Exec works with %U");

	my @exec = $entry->parse_Exec('C:/usr/share', 'http://cpan.org');
	is_deeply(\@exec,
		['fooview', '%foo', 'file:///C:/usr/share', 'http://cpan.org'],
		"parse_Exec works with %U - list context");
}

# Other keys
{
	my $entry = File::DesktopEntry->new($file);

	$entry->set(Exec => q#fooview %%foo %D#);
	my $exec = $entry->parse_Exec('/foo/bar/baz/dus/tja', './t');
	is($exec, q#fooview %foo /foo/bar/baz/dus/ ./t#,
		"parse_Exec works with %D");

	for (
		['%f', '/foo'],
		['%u', 'http://cpan.org'],
		['%d', './t']
	) {
		$entry->set(Exec => "fooview $$_[0]");
		is_deeply([$entry->parse_Exec($$_[1])], ['fooview', $$_[1]],
			"parse_Exec works with $$_[0]");
	}

	$entry->set(Exec => q#fooview %%foo %m %i %c %k#);
	$exec = $entry->parse_Exec();
	my ($f, $i, $n) = map File::DesktopEntry::_quote($_),
		$file, map $entry->get($_), qw/Icon Name/;
	is($exec, qq#fooview %foo  --icon $i $n $f#,
		"parse_Exec works with %i, %c and %k");
}

# Check errors
{
	my $entry = File::DesktopEntry->new($file);

	$entry->set(Exec => q#fooview %x#);
	eval {$entry->parse_Exec()};
	print "# message: $@\n";
	ok($@, 'parse_Exec dies on unsupported field');

	$entry->set(Exec => q#fooview %f#);
	eval {$entry->parse_Exec(qw/foo bar baz/)};
	print "# message: $@\n";
	ok($@, 'parse_Exec dies when multiple args not supported');
}

$file = File::Spec->catfile(qw/t applications rt65394.desktop/);
my $entry = File::DesktopEntry->new($file);
is($entry->get('Name'), 'caja', 'new(FILE) works');
is($entry->Name, 'caja', 'AUTOLOAD works');
is($entry->Path, '', 'Path is empty string');

done_testing;

use strict;
use warnings;

use File::DesktopEntry;

$| = 1;
#$File::DesktopEntry::VERBOSE = 1;

# Because this test runs external processes we can not use Test::More.
# Parts taking place in external processes do not show in testcover

print "1..4\n";

my $perl = $^X;

my $entry = File::DesktopEntry->new();
$entry->set(
	Name => 'test',
	Type => 'Application',
	Exec => qq#"$perl" -e 'print "ok 1 - system() works\n"'#);
#warn ">>>\n", $entry->text(), "<<<\n";
$entry->system();

$entry->set(
	Exec => qq#"$perl" -e 'print "ok 2 - run() works\n"'#
);
my $pid = $entry->run();
if ($^O eq 'MSWin32') {
		$pid->Wait(&Win32::Process::INFINITE);
}
else { waitpid($pid, 0) }

$entry->set(
	Exec => qq#"$perl" -e 'print ""'#,
	Path => 't/applications'
);
$entry->system();
print( (-f 'MANIFEST' ? 'ok' : 'nok'),
	" 3 - directory reset properly when using Path\n" );

$entry->set(
	Exec => qq#"$perl" -e 'print( (-f "foo.desktop" ? "ok" : "nok"), " 4 - exec() works using Path\n")'#
);

if ($^O eq 'MSWin32') {
	print "ok 4 # skip fork() not supported\n";
}
else {
	# not sure why, but gives ugly result on Win32
	# probably due to fork() emulation
	$pid = fork;
	unless ($pid) {
		$entry->exec();
		print "nok 4"; # not supposed to make it this far
		exit 1;
	}
	waitpid($pid, 0);
}


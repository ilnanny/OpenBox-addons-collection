use strict;
use warnings;

use 5.008_001;

use ExtUtils::MakeMaker;

WriteMakefile
(
  'NAME'               => 'File::DesktopEntry',
  'ABSTRACT'           => 'Module to handle .desktop files',
  'AUTHOR'             => 'Jaap Karssenberg <pardus@cpan.org>',
  'DISTNAME'           => "File-DesktopEntry",
  'VERSION_FROM'       => 'lib/File/DesktopEntry.pm',
  'LICENSE'            => 'perl',
  'MIN_PERL_VERSION'   => '5.8.6',
  'PREREQ_PM' => {
    'Carp'           => 0,
    'Encode'         => 0,
    'File::Spec'     => 0,
    'File::Path'     => 0,
    'File::BaseDir'  => '0.03',
    'URI::Escape'    => 0,
    ($^O eq 'MSWin32' ? ('Win32::Process' => 0) : ()),
  },
  'CONFIGURE_REQUIRES' => {
    "ExtUtils::MakeMaker" => "6.30"
  },
  'LIBS'               => [''],
  'dist' => {
    COMPRESS => "gzip -9f",
    SUFFIX => "gz",
  },
  'test' => {
    'TESTS' => "t/*.t"
  },
  META_MERGE => {
    resources => {
      repository => 'https://github.com/mbeijen/File-DesktopEntry',
      bugtracker => 'https://github.com/mbeijen/File-DesktopEntry/issues',
    },
  },
);

#!/usr/bin/perl
# Openbox menu to recursively list directories and files.
use File::Basename;
use File::Find::Rule;
use Cwd 'abs_path';
use File::Spec::Functions qw/ catdir catfile /;
use warnings;
use strict;

sub say { print "$_\n" for @_; }
sub print_browse;
sub print_bookmarks;
sub item;
sub menu;
sub fix_html (\$);

##################################################################################################
########################################## CONFIGURATION #########################################
##################################################################################################

# set default starting directory
my $base_dir = '/';
# true to show hidden files and directories
my $show_hidden = 1;
# true to show ..
my $show_up = 0;
# true to show gtk bookmarks at the top of the root menu
my $show_bookmarks = 1;
# file from which to read bookmarks
my $gtk_bookmarks_file = "$ENV{HOME}/.gtk-bookmarks";
# show 'Open in browser' entry
my $browse = 1;

##################################################################################################

# path to this script needed because it calls itself to list subdirectories
my $path = abs_path $0;
# when listing subdirectories, set the starting dir accordingly
$base_dir = abs_path $ARGV[0] if $ARGV[0];

say "<openbox_pipe_menu>";
print_browse if $browse;
print_bookmarks if $show_bookmarks && ! $ARGV[0];

if ( $show_up && $base_dir ne '/' ) {
  # replace some special characters by their html codes
  my $parent = dirname $base_dir;
  fix_html $parent;
  menu "$parent/", '..', $parent;
}

for ( sort { lc $a cmp lc $b } File::Find::Rule
      ->relative
      ->maxdepth( 1 )
      ->directory
      ->name( $show_hidden ? qr/.*/ : qr/^[^.].*/ )
      ->in( $base_dir )) {
  # replace some special characters by their html codes
  my $dir = catdir($base_dir, $_);
  fix_html $dir;
  fix_html $_;
  # replace the underscore with a double underscore in the label to
  # prevent openbox from interpreting it as a keyboard accelerator
  $_ =~ s/_/__/g;
  # escape special characters in bash
  $dir =~ s/(\ |'|`|!|\^|&amp|\*|\(|\)|\[|\]|\{|\}|&#..)/\\$1/g;
  menu $dir, $_, $dir;
}

for ( sort { lc $a cmp lc $b } File::Find::Rule
      ->relative
      ->maxdepth( 1 )
      ->file()
      ->name( $show_hidden ? qr/.*/ : qr/^[^.].*/ )
      ->in( $base_dir )) {
  # replace some special characters by their html codes
  my $file = catfile($base_dir, $_);
  fix_html $file;
  fix_html $_;
  # replace the underscore with a double underscore in the label to
  # prevent openbox from interpreting it as a keyboard accelerator
  $_ =~ s/_/__/g;
  # escape special characters in bash
  $file =~ s/(\ |'|`|!|\^|&amp|\*|\(|\)|\[|\]|\{|\}|&#..)/\\$1/g;
  item $_, $file;
}

say "</openbox_pipe_menu>";
exit 0;

##################################################################################################
########################################### SUBROUTINES ##########################################
##################################################################################################

sub print_browse {
  my $dir = shift || $base_dir;
  # replace some special characters by their html codes
  fix_html $dir;
  # escape special characters in bash
  $dir =~ s/(\ |'|`|!|\^|&amp|\*|\(|\)|\[|\]|\{|\}|&#..)/\\$1/g;
  item "Open in browser", $dir;
  say "<separator />";
}

sub print_bookmarks {
  open GTK_BKM, '<', $gtk_bookmarks_file or die "No such file $gtk_bookmarks_file\n";
  while ( <GTK_BKM> ) {
    chomp;
    $_ =~ s/^\s+|\s+$//g;	# remove leading and trailing spaces
    next unless $_;		# ignore empty lines
    
    # cannot have spaces in filenames, even if they are escaped
    my ($bookmark, $label) = ( $_ =~ m/^([^ ]+)(?:\ (.*)|$)/g );
    ## if no label was given take the base name for files
    ( $label ) = $bookmark =~ m|[^/]+$|g if $bookmark =~ m|^file://| && ! length $label;
    ## for any other urls, take the whole url
    $label = $bookmark unless length $label;
    
    # replace some special characters by their html codes
    fix_html $bookmark;
    fix_html $label;
    # replace the underscore with a double underscore in the label to
    # prevent openbox from interpreting it as a keyboard accelerator
    $label =~ s/_/__/g;
    # escape special characters in bash
    $bookmark =~ s/(\ |'|`|!|\^|&amp|\*|\(|\)|\[|\]|\{|\}|&#..)/\\$1/g;
    
    # print menu/item for directories/files and items for any other urls
    if ( $bookmark =~ s|^file://|| && ( -d $bookmark || -l $bookmark ) ) {
      menu $bookmark, $label, $bookmark;
    } else {
      item $label, $bookmark;
    }
  }
  say "<separator />";
  close GTK_BKM;
}

# print a menu for directory
sub menu {
  my $id = shift;
  my $label = shift;
  my $dir = shift;
  say "<menu id=\"$id\" label=\"$label\" execute=\"$path $dir\" />";
}

# print an item
sub item {
  my $label = shift;
  my $file = shift;
  say "  <item label=\"$label\">";
  say "    <action name=\"Execute\">";
  say "      <execute>";
  say "        xdg-open $file";
  say "      </execute>";
  say "    </action>";
  say "  </item>";
}

sub fix_html (\$) {
  my $ref = shift;
  $$ref =~ s/&/&/g;
  $$ref =~ s/"/"/g;
  $$ref =~ s/\$/$/g;
  $$ref =~ s/</</g;
  $$ref =~ s/=/=/g;
  $$ref =~ s/>/>/g;
  $$ref =~ s/\\/\/g;
}
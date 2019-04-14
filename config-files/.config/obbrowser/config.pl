#!/usr/bin/perl

# obbrowser - configuration file
# This file is updated automatically.
# Any additional comment and/or indentation will be lost.

=for comment

|| ICON SETTINGS
    | with_icons       : A true value will make the script to use icons for files and directories.
                         This option may be slow, depending on the configuration of your system.

    | mime_ext_only    : A true value will make the script to get the mimetype by extension only.
                         This will improve the performance, as no content will be read from files.

    | icon_size        : Preferred size for icons. (default: 32)
    | skip_svg_icons   : Ignore SVG icons. (default: 0)
    | force_svg_icons  : Use only SVG icons. (default: 0)
    | force_icon_size  : Use only icons at the preferred icon size, if possible. (default: 0)


|| MENU
    | file_manager     : Command to your file manager for opening files and directories.
    | browse_label     : Label for "Browse here..." action.
    | start_path       : An absolute path from which to start to browse the filesystem.
    | dirs_first       : A true value will make the script to order directories before files.

=cut

our $CONFIG = {
  browse_label    => "Browse here...",
  dirs_first      => 0,
  file_manager    => "pcmanfm",
  force_icon_size => 0,
  force_svg_icons => 0,
  icon_size       => 32,
  mime_ext_only   => 1,
  skip_svg_icons  => 0,
  start_path      => "$ENV{HOME}",
  VERSION         => 0.07,
  with_icons      => 1,
}
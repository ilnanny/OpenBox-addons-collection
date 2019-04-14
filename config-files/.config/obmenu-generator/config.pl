#!/usr/bin/perl

# obmenu-generator - configuration file
# This file will be updated automatically.
# Any additional comment and/or indentation will be lost.

=for comment

|| FILTERING
    | skip_filename_re    : Skip a .desktop file if its name matches the regex.
                            Name is from the last slash to the end. (filename.desktop)
                            Example: qr/^(?:gimp|xterm)\b/,    # skips 'gimp' and 'xterm'

    | skip_entry          : Skip a desktop file if the value from a given key matches the regex.
                            Example: [
                                {key => 'Name', re => qr/(?:about|terminal)/i},
                                {key => 'Exec', re => qr/^xterm/},
                            ],

    | substitutions       : Substitute, by using a regex, in the values of the desktop files.
                            Example: [
                                {key => 'Exec', re => qr/xterm/, value => 'sakura'},
                                {key => 'Exec', re => qr/\\\\/,  value => '\\', global => 1},    # for wine apps
                            ],

|| ICON SETTINGS
    | gtk_rc_filename     : Absolute path to the GTK configuration file.
    | missing_icon        : Use this icon for missing icons (default: gtk-missing-image)
    | icon_size           : Preferred size for icons. (default: 32)
    | force_svg_icons     : Use only SVG icons. (default: 0)
    | force_icon_size     : Use only icons at the preferred icon size, if possible. (default: 0)

|| KEYS
    | name_keys           : Valid keys for application name.
                            Example: ['Name[fr]', 'GenericName[fr]', 'Name'],   # french menu

|| PATHS
    | desktop_files_paths   : Absolute paths which contain .desktop files.
                              Example: [
                                '/usr/share/applications',
                                "$ENV{HOME}/.local/share/applications",
                                glob("$ENV{HOME}/.local/share/applications/wine/Programs/*"),
                              ],

|| NOTES
    | Regular expressions:
        * use qr/.../ instead of '...'
        * use qr/.../i for case insensitive mode

=cut

our $CONFIG = {
  "editor"              => "geany",
  "force_icon_size"     => 0,
  "force_svg_icons"     => 0,
  "gtk_rc_filename"     => "$ENV{HOME}/.gtkrc-2.0",
  "icon_size"           => 32,
  "Linux::DesktopFiles" => {
                             desktop_files_paths     => [
                                                          "/usr/share/applications",
                                                          "/usr/local/share/applications",
                                                          "$ENV{HOME}/.local/share/applications",
                                                          "$ENV{HOME}/Desktop",
                                                        ],
                             keep_unknown_categories => 1,
                             skip_entry              => [
                                                          {
                                                            key => "Name",
                                                            re  => qr/^(?:Avahi|Qt4?\b|Hardware Locality|File Manager|HDSP)/,
                                                          },
                                                        ],
                             skip_filename_re        => qr/^(?:exo-|xfce4-about|Terminal|avahi|b(?:ssh|vnc)|dconf|ffadomixer|gconf|mplayer|sakura|compton)/,
                             substitutions           => [
                                                          { global => 1, key => "Exec", re => qr/\\\\/, value => "\\" },
                                                        ],
                             terminalization_format  => "%s -e '%s'",
                             terminalize             => 1,
                             unknown_category_key    => "other",
                           },
  "missing_icon"        => "gtk-missing-image",
  "name_keys"           => ["Name"],
  "terminal"            => "sakura",
  "VERSION"             => "0.80",
}

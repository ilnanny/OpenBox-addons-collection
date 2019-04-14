#!/usr/bin/perl

# menutray - schema file

=for comment

    item:       add an item inside the menu               {item => ['command', 'label', 'icon']},
    cat:        add a category inside the menu             {cat => ['name', 'label', 'icon']},
    sep:        horizontal line separator                  {sep => undef},
    beg:        beginning of a submenu                     {beg => ['name', 'icon']},
    end:        end of a submenu                           {end => undef},
    menutray:   generic menu settings                 {menutray => ['label', 'icon']},
    regenerate: regenerate menu                     {regenerate => ['label', 'icon']},
    exit:       quit menu                                 {exit => ['label', 'icon']},

=cut

# NOTE:
#    * Keys and values are case sensitive. Keep all keys lowercase.
#    * ICON can be a either a direct path to an icon or a valid icon name
#    * Category names are case insensitive. (X-XFCE and x_xfce are equivalent)

our $SCHEMA = [
    #          COMMAND                 LABEL                   ICON
    {item => ['xdg-open .',        'File Manager',    'system-file-manager']},
    {item => ['xterm',             'Terminale',       'utilities-terminal']},
    {item => ['xdg-open http://',  'Browser Web',     'web-browser']},
    {item => ['gmrun',             'Esegui ',         'system-run']},

    {sep => undef},

    #          NAME            LABEL                ICON
    {cat => ['utility',     'Accessori',    'applications-utilities']},
    {cat => ['development', 'Sviluppo',     'applications-development']},
    {cat => ['education',   'Istruzione',   'applications-science']},
    {cat => ['game',        'Giochi',       'applications-games']},
    {cat => ['graphics',    'Grafica',      'applications-graphics']},
    {cat => ['audiovideo',  'Multimedia',   'applications-multimedia']},
    {cat => ['network',     'Rete',         'applications-internet']},
    {cat => ['office',      'Ufficio',      'applications-office']},
    {cat => ['other',       'Altro',        'applications-other']},
    {cat => ['settings',    'Impostazioni', 'applications-accessories']},
    {cat => ['system',      'Sistema',      'applications-system']},

    #              LABEL          ICON
    #{beg => ['My submenu',  'submenu-icon']},
              #...some items here...#
    #{end => undef},

    {menutray   => ['Menutray', 'preferences-desktop']},

    {sep        => undef},
    {regenerate => ['Rigenera', 'gtk-refresh']},
    {exit       => ['Esci', 'application-exit']},
];

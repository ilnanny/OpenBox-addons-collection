# ~/.inputrc

$include /etc/inputrc

set editing-mode vi
set show-mode-in-prompt On

$if Bash
    SPACE: magic-space
$endif

$if term=linux
    set vi-ins-mode-string \1\e[?0c\2
    set vi-cmd-mode-string \1\e[?8c\2
$else
    set vi-ins-mode-string \1\e[6 q\2
    set vi-cmd-mode-string \1\e[2 q\2
$endif

$if mode=vi
    set keymap vi-command
    j: history-search-forward
    k: history-search-backward
    "\e[A": history-search-backward
    "\e[B": history-search-forward

    set keymap vi-insert
    TAB: menu-complete
    "\e[Z": menu-complete-backward
    "\e[A": history-search-backward
    "\e[B": history-search-forward
    "\e[1;5D": backward-word
    "\e[1;5C": forward-word
    "\C-l": clear-screen
    "\C-r": vi-redo
    "\C-a": beginning-of-line
    "\C-e": end-of-line
    "\C-w":backward-kill-word

    # Ctrl-Space expands the alias to the left of the cursor
    "\C-@": alias-expand-line

    # Alt-Enter sends a linebreak
    "\e\C-m": "\026\n"
$endif

# tab completion menu settings
set colored-stats On
set visible-stats On
set page-completions Off
set skip-completed-text On
set show-all-if-ambiguous On
set completion-ignore-case On
set enable-bracketed-paste On
set echo-control-characters Off
set colored-completion-prefix On
set mark-symlinked-directories On
set menu-complete-display-prefix On
set print-completions-horizontally On

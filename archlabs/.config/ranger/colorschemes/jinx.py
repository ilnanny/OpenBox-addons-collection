"""
A ranger color scheme

Made to be eye catchy while maintaining visibility, and base 0-7 colours.

Inspired by themes like Tomorrow, Dracula, Atom, and Spacemacs, but with my own twists
"""

from ranger.gui.colorscheme import ColorScheme
from ranger.gui.color import *


class jinx(ColorScheme):
    """
    Defines colours used when colourscheme is enabled
    """
    progress_bar_color = 96

    def use(self, context):
        """
        Main colour block with individual definitions
        """
        fg, bg, attr = default_colors

        if context.reset:
            return default_colors
        elif context.in_browser:
            if context.selected:
                attr = reverse
            else:
                attr = normal
            if context.empty or context.error:
                fg = 131
            if context.border:
                fg = 247
            if context.image:
                fg = 179
            if context.video:
                fg = 96
            if context.audio:
                fg = 117
            if context.document:
                fg = 38
            if context.container:
                fg = 108
            if context.directory:
                fg = 103
            elif context.executable and not \
                    any((context.media, context.fifo, context.container, context.socket)):
                fg = 67
            if context.socket:
                fg = 179
                attr |= bold
            if context.fifo or context.device:
                fg = 214
                attr |= bold
            if context.link:
                fg = 38 if context.good else 131
            if context.tag_marker and not context.selected:
                fg = 96
                attr |= bold
            if not context.selected and (context.cut or context.copied):
                fg = 247
                attr |= underline
            if context.main_column:
                if context.marked:
                    attr |= underline
                    fg = 131
                if context.selected:
                    attr |= normal
            if context.badinfo:
                if attr & reverse:
                    bg = 96
                else:
                    fg = 203
        elif context.in_titlebar:
            attr |= bold
            if context.hostname:
                fg = 203 if context.bad else 67
            elif context.directory:
                fg = 96
            elif context.tab:
                if context.good:
                    bg = 96
                elif context.link:
                    fg = 117
        elif context.in_statusbar:
            if context.permissions:
                if context.good:
                    fg = 67
                elif context.bad:
                    fg = 203
            if context.marked:
                attr |= bold | reverse
                fg = 96
            if context.message:
                if context.bad:
                    attr |= bold
                    fg = 96
            if context.loaded:
                bg = self.progress_bar_color
            if context.vcsinfo:
                fg = 38
                attr &= ~bold
            if context.vcscommit:
                fg = 108
                attr &= ~bold
        if context.text:
            fg = 254
            if context.highlight:
                attr |= reverse
        if context.in_taskview:
            if context.title:
                fg = 67
            if context.selected:
                attr |= reverse
            if context.loaded:
                if context.selected:
                    fg = self.progress_bar_color
                else:
                    bg = self.progress_bar_color
        if context.vcsfile and not context.selected:
            attr &= ~bold
            if context.vcsconflict:
                fg = 203
            elif context.vcschanged:
                fg = 174
            elif context.vcsunknown:
                fg = 174
            elif context.vcsstaged:
                fg = 108
            elif context.vcssync:
                fg = 108
            elif context.vcsignored:
                fg = default
        elif context.vcsremote and not context.selected:
            attr &= ~bold
            if context.vcssync:
                fg = 108
            elif context.vcsbehind:
                fg = 174
            elif context.vcsahead:
                fg = 67
            elif context.vcsdiverged:
                fg = 203
            elif context.vcsunknown:
                fg = 174

        return fg, bg, attr

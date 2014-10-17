#!/usr/bin/env python

import urwid

def handle_input(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

palette = [
        ('highlight', 'black', 'brown'),
        ]

shortcuts = urwid.Text(('highlight', ' q: Quit'))
shortcuts_wrapper = urwid.AttrMap(shortcuts, 'highlight')

pile = urwid.Pile([
    urwid.Filler(shortcuts_wrapper),
    ])

main = urwid.Frame(pile)

loop = urwid.MainLoop(main, palette=palette, unhandled_input=handle_input)
loop.screen.set_terminal_properties(colors=16)
loop.run()

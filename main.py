#!/usr/bin/env python

import urwid

class VMWidget (urwid.WidgetWrap):

    def __init__ (self, state, name):
        self.state = state
        self.content = name
        self.item = urwid.AttrMap(
                urwid.Text('%-15s  %s' % (state, name)), 'body', 'focus'
                )
        self.__super.__init__(self.item)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key


def handle_input(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

    elif key in ('j'):
        try:
            listbox.set_focus(listbox.focus_position + 1)
        except IndexError:
            pass

    elif key in ('k'):
        try:
            listbox.set_focus(listbox.focus_position - 1)
        except IndexError:
            pass

palette = [
        ('highlight', 'black', 'brown'),
        ('body','dark cyan', ''),
        ('focus','dark red', 'black'),
        ]

vms = 'foo lkj kj lskjdf jlklekj f'.split()

shortcuts = urwid.AttrMap(urwid.Text(' q: Quit'), 'highlight')
listbox = urwid.ListBox(urwid.SimpleListWalker([VMWidget('foo', v) for v in vms]))
label = urwid.AttrMap(urwid.Text(' VM Selection'), 'highlight')

main = urwid.Frame(urwid.AttrMap(listbox, 'body'), header=shortcuts, \
        footer=label)

loop = urwid.MainLoop(main, palette=palette, unhandled_input=handle_input)
loop.screen.set_terminal_properties(colors=16)
loop.run()

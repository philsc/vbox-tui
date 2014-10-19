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

def switch_list(listbox):
    global current_listbox
    current_listbox = listbox
    main.contents.update(body=(listbox, None))

def handle_input(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

    elif key in ('j',):
        try:
            current_listbox.set_focus(current_listbox.focus_position + 1)
        except IndexError:
            pass

    elif key in ('k',):
        try:
            current_listbox.set_focus(current_listbox.focus_position - 1)
        except IndexError:
            pass

    elif key in ('e',):
        if current_listbox is listbox_props:
            switch_list(listbox_vms)
        else:
            switch_list(listbox_props)

palette = [
        ('highlight', 'black', 'brown'),
        ('body','dark cyan', ''),
        ('focus','dark red', 'black'),
        ]

vms = 'foo lkj kj lskjdf jlklekj f'.split()

listbox_vms = urwid.ListBox(urwid.SimpleListWalker( \
        [VMWidget('foo', v) for v in vms]))
listbox_props = urwid.ListBox(urwid.SimpleListWalker( \
        [VMWidget('barr', v + ' me') for v in vms]))

current_listbox = listbox_vms

shortcuts = urwid.AttrMap(urwid.Text(' q: Quit'), 'highlight')
listbox_vms_map = urwid.AttrMap(listbox_vms, 'body')
listbox_props_map = urwid.AttrMap(listbox_props, 'body')
label = urwid.AttrMap(urwid.Text(' VM Selection'), 'highlight')

main = urwid.Frame(listbox_vms_map, header=shortcuts, footer=label)

loop = urwid.MainLoop(main, palette=palette, unhandled_input=handle_input)
loop.screen.set_terminal_properties(colors=16)
loop.run()

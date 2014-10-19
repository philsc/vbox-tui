#!/usr/bin/env python

import urwid
import subprocess
import shlex
import re

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

class VBox(object):
    command = 'VBoxManage'

    def vms(self):
        out = self._cmd('list vms')
        vms = []

        for line in out.splitlines():
            m = re.search(r'"([a-zA-Z0-9-_]+)"', line)
            if m:
                name = m.group(1)
                state = self.state(name)
                vms.append((state, name))

        return vms

    def state(self, name):
        out = self._cmd('showvminfo ' + name)

        for line in out.splitlines():
            if line.startswith('State:'):
                m = re.search(r'State:\s+([^(]+) \(', out)
                if m: return m.group(1)

        raise Exception('Could not find state for VM "%s".' % name)

    def _cmd(self, cmd):
        out = subprocess.check_output([self.command] + shlex.split(cmd))
        return out.decode('utf-8')

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

vbox = VBox()
vms = vbox.vms()

listbox_vms = urwid.ListBox(urwid.SimpleListWalker( \
        [VMWidget(v[0], v[1]) for v in vms]))
listbox_props = urwid.ListBox(urwid.SimpleListWalker( \
        [VMWidget('barr', v[1] + ' me') for v in vms]))

current_listbox = listbox_vms

shortcuts = urwid.AttrMap(urwid.Text(' q: Quit'), 'highlight')
listbox_vms_map = urwid.AttrMap(listbox_vms, 'body')
listbox_props_map = urwid.AttrMap(listbox_props, 'body')
label = urwid.AttrMap(urwid.Text(' VM Selection'), 'highlight')

main = urwid.Frame(listbox_vms_map, header=shortcuts, footer=label)

loop = urwid.MainLoop(main, palette=palette, unhandled_input=handle_input)
loop.screen.set_terminal_properties(colors=16)
loop.run()

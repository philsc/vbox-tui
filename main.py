#!/usr/bin/env python

import urwid
import subprocess
import shlex
import re

class EditDialog(urwid.WidgetWrap):

    signals = ['close']

    def __init__(self, parent):
        self.parent = parent
        self.label = urwid.Text("Edit dialog!")
        self.edit = urwid.Edit(edit_text=parent.value)
        pile = urwid.Pile([self.label, self.edit])
        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))

    def keypress(self, size, key):
        if key in ('enter',):
            self.parent.update_value(self.edit.edit_text)
            self._emit('close')
        else:
            self.__super.keypress(size, key)

class VMWidget (urwid.WidgetWrap):

    def __init__ (self, state, name):
        self.state = state
        self.name = name
        self.item = urwid.AttrMap(
                urwid.Text('%-15s  %s' % (state, name)), 'body', 'focus'
                )
        self.__super.__init__(self.item)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

class PropWidget(urwid.PopUpLauncher):

    def __init__(self, prop, value):
        self.prop = prop
        self.value = None
        self.item = urwid.AttrMap(urwid.Text('placeholder'), 'body', 'focus')
        self.update_value(value)
        self.__super.__init__(self.item)

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key in ('e',):
            self.open_pop_up()
        else:
            return key

    def create_pop_up(self):
        pop_up = EditDialog(self)
        urwid.connect_signal(pop_up, 'close',
                lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}

    def update_value(self, new_value):
        self.value = new_value
        self.item.original_widget.set_text(' %15s:  %s' % (self.prop, self.value))


class VBox(object):
    command = 'VBoxManage'

    PROPERTIES = [
            'Guest OS',
            'Number of CPUs',
            'Memory size',
            'VRAM size',
            ]

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

    def properties(self, name):
        out = self._cmd('showvminfo ' + name)

        # Create a copy of the properties list so we can modify it.
        property_names = list(self.PROPERTIES)
        props = {}

        for line in out.splitlines():
            for prop_name in property_names:
                if line.startswith(prop_name):
                    m = re.search(r'%s:\s+(.+)' % prop_name, line)
                    if m: props[prop_name] = m.group(1)

        return props

    def state(self, name):
        out = self._cmd('showvminfo ' + name)
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
            vm = current_listbox.focus
            if vm:
                props = vbox.properties(vm.name)
                listwalker_props[:] = [PropWidget(k, props[k]) for k in props]
                switch_list(listbox_props)

palette = [
        ('highlight', 'black', 'brown'),
        ('body','dark cyan', ''),
        ('focus','dark red', 'black'),
        ('popbg', 'white', 'dark blue'),
        ]

vbox = VBox()
vms = vbox.vms()

listwalker_vms = urwid.SimpleListWalker([VMWidget(v[0], v[1]) for v in vms])
listwalker_props = urwid.SimpleListWalker([])

listbox_vms = urwid.ListBox(listwalker_vms)
listbox_props = urwid.ListBox(listwalker_props)

current_listbox = listbox_vms

shortcuts_text = urwid.Text(' q: Quit')
label_text = urwid.Text(' VM Selection')



shortcuts = urwid.AttrMap(shortcuts_text, 'highlight')
listbox_vms_map = urwid.AttrMap(listbox_vms, 'body')
listbox_props_map = urwid.AttrMap(listbox_props, 'body')
label = urwid.AttrMap(label_text, 'highlight')

main = urwid.Frame(listbox_vms_map, header=shortcuts, footer=label)

loop = urwid.MainLoop(main, palette=palette, unhandled_input=handle_input, \
        pop_ups=True)
loop.screen.set_terminal_properties(colors=16)
loop.run()

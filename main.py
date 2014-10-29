#!/usr/bin/env python3

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

        elif key in ('esc',):
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
        if key in ('e', 'enter', 'l'):
            window.new_screen('props', [self.name])

        elif key in ('u',):
            window.new_screen('usb', [self.name])

        else:
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
        if key in ('e', 'l'):
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

class USBWidget(urwid.WidgetWrap):

    def __init__(self, vm_name, attributes):
        self.vm_name = vm_name
        self.attributes = attributes
        self.item = urwid.AttrMap(urwid.Text(''), 'body', 'focus')
        self._update_text()
        self.__super.__init__(self.item)

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key in (' ', 'enter', 'l'):
            if self.attributes['Current State'] != 'Busy':
                if self.attributes['AttachedToThisVM']:
                    action = 'detach'
                else:
                    action = 'attach'

                try:
                    vbox.modify_usb(self.vm_name, action, \
                            self.attributes['UUID'])
                except:
                    return

                self.attributes['AttachedToThisVM'] ^= True
                self._update_text()

        return key

    def _update_text(self):
        name = self.attributes['Product']

        if self.attributes['Current State'] == 'Busy':
            selector = ''
        elif self.attributes['AttachedToThisVM']:
            selector = '(x)'
        else:
            selector = '( )'

        self.item.original_widget.set_text(' %-3s %s' % (selector, name))


class VBox(object):
    command = 'VBoxManage'

    PROPERTIES = [
            'Guest OS',
            'Number of CPUs',
            'Memory size',
            'VRAM size',
            ]

    USB_PARSER = [
            ('UUID', '([a-zA-Z0-9-]+)'),
            ('VendorId', '.*\((.*)\)$'),
            ('ProductId', '.*\((.*)\)$'),
            ('Product', '(.*)$'),
            ('Current State', '(.*)'),
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

    def usb_list(self, name):
        out_usb = self._cmd('list usbhost')
        out_info = self._cmd('showvminfo ' + name)

        vm_uuids = []
        usb_devices = []

        current_usb_device = dict([(k[0], None) for k in self.USB_PARSER])

        for line in out_info.splitlines():
            m = re.search(r'^UUID:\s+([a-zA-Z0-9-]+)', line)
            if m: vm_uuids.append(m.group(1))

        for line in out_usb.splitlines():
            for usb_field in self.USB_PARSER:
                if line.startswith(usb_field[0] + ':'):
                    m = re.search(r'%s:\s+%s' % usb_field, line)
                    if m:
                        current_usb_device[usb_field[0]] = m.group(1)

                    # Once we've parsed all fields for one USB device, save it.
                    if usb_field[0] == self.USB_PARSER[-1][0]:
                        current_usb_device['AttachedToThisVM'] = \
                                current_usb_device['UUID'] in vm_uuids
                        usb_devices.append(current_usb_device.copy())

        return usb_devices

    def modify_usb(self, vm_name, action, usb_uuid):
        if not action in ('attach', 'detach'): return

        out = self._cmd('controlvm %s usb%s %s' % (vm_name, action, usb_uuid))

    def _cmd(self, cmd):
        out = subprocess.check_output([self.command] + shlex.split(cmd))
        return out.decode('utf-8')


class Screen(object):

    def __init__(self, generator):
        self.generator = generator
        self.listwalker = urwid.SimpleListWalker([])

    def update(self, args):
        self.listwalker[:] = self.generator(args)

    def get_current(self):
        vm = self.listwalker.focus
        if vm:
            return self.listwalker[vm].name

        raise Exception('Could not determine current focus')


class Window(object):

    def __init__(self, screens, first_screen):
        self.shortcuts_text = urwid.Text(' q: Quit / r: Refresh')
        self.label_text = urwid.Text(' VM Selection')
        self.shortcuts = urwid.AttrMap(self.shortcuts_text, 'highlight')
        self.label = urwid.AttrMap(self.label_text, 'highlight')

        nil_screen = {'__nil__': Screen(lambda _: [])}
        self.screens = dict(screens.items() | nil_screen.items())
        self.screen_stack = [('__nil__', [])]

        palette = [
                ('highlight', 'black', 'brown'),
                ('body','dark cyan', ''),
                ('focus','dark red', 'black'),
                ('popbg', 'white', 'dark blue'),
                ]

        self.main = urwid.Frame(urwid.Text(''), header=self.shortcuts, 
                footer=self.label)

        self.loop = urwid.MainLoop(self.main, palette=palette, \
                unhandled_input=self.handle_input, pop_ups=True)
        self.loop.screen.set_terminal_properties(colors=16)

        self._switch('__nil__', [])
        self.new_screen(first_screen, [])

    def wrap_listwalker(self, listwalker):
        return urwid.AttrMap(urwid.ListBox(listwalker), 'body')

    def move_selection(self, count):
        listbox = self.main.contents['body'][0].original_widget
        try:
            listbox.set_focus(listbox.focus_position + count)
        except IndexError:
            pass

    def new_screen(self, next_screen, args):
        self.screen_stack.append((self.current_screen, self.current_args))
        self._switch(next_screen, args)

    def last_screen(self):
        if self.screen_stack[-1][0] == '__nil__':
            return

        screen, args = self.screen_stack.pop()
        self._switch(screen, args)

    def _switch(self, screen, args):
        self.current_screen = screen
        self.current_args = args
        self.screens[screen].update(args)

        listbox = self.wrap_listwalker(self.screens[screen].listwalker)
        self.main.contents.update(body=(listbox, None))

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        if key in ('r', 'R'):
            self.screens[self.current_screen].update(self.current_args)

        elif key in ('j',):
            self.move_selection(1)

        elif key in ('k',):
            self.move_selection(-1)

        elif key in ('h', 'esc'):
            self.last_screen()

    def run(self):
        self.loop.run()


vbox = VBox()

def update_vms(_):
    return [VMWidget(v[0], v[1]) for v in vbox.vms()]

def update_props(args):
    vm_name = args[0]
    return [PropWidget(k, v) for k,v in vbox.properties(vm_name).items()]

def update_usb_list(args):
    vm_name = args[0]
    return [USBWidget(vm_name, attributes) for attributes in \
            vbox.usb_list(vm_name)]

screens = {
        'vm': Screen(update_vms),
        'props': Screen(update_props),
        'usb': Screen(update_usb_list),
        }

window = Window(screens, 'vm')
window.run()
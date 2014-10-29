vbox-tui
========
Text-based UI frontend to VirtualBox' command line tools.


Requirements
============
- Python 3.x
- Urwid Library (<http://urwid.org>)

I would recommend to grab the latest urwid library via ``pip`` or your other 
favourite python package manager. I've been having trouble with the version 
that is packaged in the Ubuntu 14.04 repositories.

.. code:: sh

   pip install urwid


Usage
=====

.. code:: sh

   git clone https://github.com/philsc/vbox-tui.git
   cd vbox-tui
   ./main.py

Even though the window doesn't say so, you can hit the ``u`` key to access the 
USB view of a VM. Attach and detach USB devices with Space or Enter.


Limitations
===========
- Currently the TUI can only attach and detach USB devices.


TODO
====
- Actually let people modify values such as Memory, CPUs, etc..
- Make the shortcuts pane (at the top of the screen) and the label pane (at the 
  bottom of the screen) adjustable on a per-screen basis.

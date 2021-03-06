vbox-tui
========
Text-based UI frontend to VirtualBox' command line tools.


Requirements
============
- Python 2.7+ or 3.2+
- Urwid Library (http://urwid.org)

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

You can hit the ``u`` key to access the USB view of a VM. Attach and detach USB 
devices with Space or Enter.


Limitations
===========
- Currently the TUI can only attach and detach USB devices. That was really the 
  original goal of the project.


TODO
====
- Let people start/stop/suspend VMs from the main screen.
- Actually let people modify values such as Memory, CPUs, etc..
- Make the shortcuts pane (at the top of the screen) and the label pane (at the 
  bottom of the screen) adjustable on a per-screen basis.
- Make use of the official vboxapi Python module. I can't believe I didn't find 
  this when I first started working on this project.

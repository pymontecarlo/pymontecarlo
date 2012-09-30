#!/usr/bin/env python
"""
================================================================================
:mod:`config_gui` -- Base configuration of the graphical user interface
================================================================================

.. module:: config_gui
   :synopsis: Base configuration of the graphical user interface

.. inheritance-diagram:: pymontecarlo.program.config_gui

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import wx
from wx.lib.scrolledpanel import ScrolledPanel

# Local modules.

# Globals and constants variables.

class ConfigurePanel(ScrolledPanel):

    def __init__(self, parent, program, settings):
        ScrolledPanel.__init__(self, parent)

        # Variables
        self._program = program

        # Controls
        lbl_program = wx.StaticText(self, label=program.name)
        font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
        lbl_program.SetFont(font)

        # Sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(lbl_program, 0, wx.BOTTOM, 10)

        self.SetSizer(mainsizer)

        # Extra controls
        self._create_controls(mainsizer, settings)

        self.SetupScrolling(False, True)

    def _create_controls(self, sizer, settings):
        """
        Adds extra controls to the panel.
        """
        lbl_none = wx.StaticText(self, label='No configuration required')
        sizer.Add(lbl_none, 0)

    def save(self, settings):
        """
        Validates and saves the information from this panel in the settings.
        Returns ``True`` if the information were valid, ``False`` otherwise.
        """
        settings.add_section(self._program.alias)
        return True

class GUI(object):

    def create_configure_panel(self, parent, settings):
        """
        Returns the configure panel for this program.
        
        :arg parent: parent window
        :arg settings: settings object
        """
        raise NotImplementedError

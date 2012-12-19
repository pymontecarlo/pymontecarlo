#!/usr/bin/env python
"""
================================================================================
:mod:`config_gui` -- Monaco Monte Carlo program GUI configuration
================================================================================

.. module:: config_gui
   :synopsis: Monaco Monte Carlo program GUI configuration

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.
import wx

# Local modules.
from pymontecarlo.program.config_gui import GUI, ConfigurePanel
from pymontecarlo.program.monaco.config import program

from wxtools2.browse import DirBrowseCtrl
from wxtools2.dialog import show_error_dialog

# Globals and constants variables.

class _MonacoConfigurePanel(ConfigurePanel):

    def _create_controls(self, sizer, settings):
        # Controls
        lbl_basedir = wx.StaticText(self, label='Full path to base directory')

        self._brw_basedir = DirBrowseCtrl(self)

        # Sizer
        sizer.Add(lbl_basedir, 0)
        sizer.Add(self._brw_basedir, 0, wx.GROW)

        # Values
        if 'monaco' in settings:
            path = getattr(settings.monaco, 'basedir', None)
            try:
                self._brw_basedir.SetPath(path)
            except ValueError:
                pass

    def Validate(self):
        if not ConfigurePanel.Validate(self):
            return False

        basedir = self._brw_basedir.GetPath()
        if not basedir:
            show_error_dialog(self, 'Please specify the base directory')
            return False

        mcsim32_exe = os.path.join(basedir, 'Mcsim32.exe')
        if not os.path.isfile(mcsim32_exe):
            show_error_dialog(self, "No Mcsim32.exe in Monaco base directory (%s)" % basedir)
            return False

        mccli32_exe = os.path.join(basedir, 'Mccli32.exe')
        if not os.path.isfile(mccli32_exe):
            show_error_dialog(self, "No Mccli32.exe in Monaco base directory (%s)" % basedir)
            return False

        return True

    def save(self, settings):
        section = settings.add_section('monaco')
        section.basedir = self._brw_basedir.GetPath()

class _MonacoGUI(GUI):

    def create_configure_panel(self, parent, settings):
        """
        Returns the configure panel for this program.
        
        :arg parent: parent window
        :arg settings: settings object
        """
        return _MonacoConfigurePanel(parent, program, settings)

gui = _MonacoGUI()

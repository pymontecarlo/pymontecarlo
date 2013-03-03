#!/usr/bin/env python
"""
================================================================================
:mod:`config_gui` -- WinXRay Monte Carlo program GUI configuration
================================================================================

.. module:: config_gui
   :synopsis: WinXRay Monte Carlo program GUI configuration

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

# Local modules.
from pymontecarlo.program.config_gui import GUI, ConfigurePanel
from pymontecarlo.program.winxray.config import program

from wxtools2.browse import FileBrowseCtrl
from wxtools2.dialog import show_error_dialog

# Globals and constants variables.

class _WinXRayConfigurePanel(ConfigurePanel):

    def _create_controls(self, sizer, settings):
        # Controls
        lbl_exe = wx.StaticText(self, label='Full path to WinXRay.exe')

        filetypes = [('Application files (*.exe)', 'exe')]
        self._brw_exe = FileBrowseCtrl(self, filetypes=filetypes)

        # Sizer
        sizer.Add(lbl_exe, 0)
        sizer.Add(self._brw_exe, 0, wx.GROW)

        # Values
        if 'winxray' in settings:
            path = getattr(settings.winxray, 'exe', None)
            try:
                self._brw_exe.SetPath(path)
            except ValueError:
                pass

    def Validate(self):
        if not ConfigurePanel.Validate(self):
            return False

        if not self._brw_exe.GetPath():
            show_error_dialog(self, 'Please specify the WinXRay path')
            return False

        return True

    def save(self, settings):
        section = settings.add_section('winxray')
        section.exe = self._brw_exe.GetPath()

class _WinXRayGUI(GUI):

    def create_configure_panel(self, parent, settings):
        """
        Returns the configure panel for this program.
        
        :arg parent: parent window
        :arg settings: settings object
        """
        return _WinXRayConfigurePanel(parent, program, settings)

gui = _WinXRayGUI()

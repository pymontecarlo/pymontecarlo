#!/usr/bin/env python
"""
================================================================================
:mod:`config_gui` -- PENEPMA Monte Carlo program GUI configuration
================================================================================

.. module:: config_gui
   :synopsis: PENEPMA Monte Carlo program GUI configuration

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import platform

# Third party modules.
import wx

# Local modules.
from pymontecarlo.program.config_gui import GUI, ConfigurePanel
from pymontecarlo.program.penepma.config import program

from wxtools2.browse import FileBrowseCtrl, DirBrowseCtrl, EVT_BROWSE
from wxtools2.dialog import show_error_dialog
from wxtools2.floatspin import FloatSpin

# Globals and constants variables.

class _PenepmaConfigurePanel(ConfigurePanel):

    def _create_controls(self, sizer, settings):
        # Controls
        lbl_pendbase = wx.StaticText(self, label='Path to pendbase directory')
        self._brw_pendbase = DirBrowseCtrl(self)

        lbl_exe = wx.StaticText(self, label='Path to PENEPMA executable')

        if platform.system() == 'Windows':
            filetypes = [('Application files', 'exe')]
        else:
            filetypes = [('Application files', '*')]
        self._brw_exe = FileBrowseCtrl(self, filetypes=filetypes)

        lbl_dumpp = wx.StaticText(self, label='Interval between dump (s)')

        self._fs_dumpp = FloatSpin(self, min_val=30)

        # Sizer
        sizer.Add(lbl_pendbase, 0)
        sizer.Add(self._brw_pendbase, 0, wx.GROW)
        sizer.Add(lbl_exe, 0, wx.TOP, 10)
        sizer.Add(self._brw_exe, 0, wx.GROW)
        sizer.Add(lbl_dumpp, 0, wx.TOP, 10)
        sizer.Add(self._fs_dumpp, 0, wx.GROW)

        # Bind
        self.Bind(EVT_BROWSE, self.OnBrowse, self._brw_pendbase)
        self.Bind(EVT_BROWSE, self.OnBrowse, self._brw_exe)

        # Values
        if 'penepma' in settings:
            path = getattr(settings.penepma, 'pendbase', None)
            try:
                self._brw_pendbase.SetPath(path)
            except ValueError:
                pass

            path = getattr(settings.penepma, 'exe', None)
            try:
                self._brw_exe.SetPath(path)
            except ValueError:
                pass

            try:
                dumpp = int(getattr(settings.penepma, 'dumpp', 30))
                self._fs_dumpp.SetValue(dumpp)
            except (TypeError, ValueError):
                pass

    def OnBrowse(self, event):
        self._brw_pendbase.SetBaseDir(event.path)
        self._brw_exe.SetBaseDir(event.path)

    def Validate(self):
        if not ConfigurePanel.Validate(self):
            return False

        if not self._brw_pendbase.GetPath():
            show_error_dialog(self, 'Please specify a pendbase directory')
            return False

        if not self._brw_exe.GetPath():
            show_error_dialog(self, 'Please specify the PENEPMA executable')
            return False
        if not os.access(self._brw_exe.GetPath(), os.X_OK):
            show_error_dialog(self, 'Specified file is not executable')
            return False

        return True

    def save(self, settings):
        section = settings.add_section('penepma')
        section.pendbase = self._brw_pendbase.GetPath()
        section.exe = self._brw_exe.GetPath()
        section.dumpp = int(self._fs_dumpp.GetValue())

class _PenepmaGUI(GUI):

    def create_configure_panel(self, parent, settings):
        """
        Returns the configure panel for this program.
        
        :arg parent: parent window
        :arg settings: settings object
        """
        return _PenepmaConfigurePanel(parent, program, settings)

gui = _PenepmaGUI()

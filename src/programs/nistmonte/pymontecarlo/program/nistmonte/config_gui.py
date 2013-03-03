#!/usr/bin/env python
"""
================================================================================
:mod:`config_gui` -- NISTMonte Monte Carlo program GUI configuration
================================================================================

.. module:: config_gui
   :synopsis: NISTMonte Monte Carlo program GUI configuration

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import platform

# Third party modules.
import wx

# Local modules.
from pymontecarlo.program.config_gui import GUI, ConfigurePanel
from pymontecarlo.program.nistmonte.config import program

from wxtools2.browse import FileBrowseCtrl, EVT_BROWSE
from wxtools2.dialog import show_error_dialog

# Globals and constants variables.

class _NistMonteConfigurePanel(ConfigurePanel):

    def _create_controls(self, sizer, settings):
        # Controls
        lbl_java = wx.StaticText(self, label='Path to Java executable')

        if platform.system() == 'Windows':
            filetypes = [('Application files', 'exe')]
        else:
            filetypes = [('Application files', '*')]
        self._brw_java = FileBrowseCtrl(self, filetypes=filetypes)

        lbl_jar = wx.StaticText(self, label='Path to pymontecarlo-nistmonte jar')

        filetypes = [('Jar files (*.jar)', 'jar')]
        self._brw_jar = FileBrowseCtrl(self, filetypes=filetypes)

        # Sizer
        sizer.Add(lbl_java, 0)
        sizer.Add(self._brw_java, 0, wx.GROW)
        sizer.Add(lbl_jar, 0, wx.TOP, 10)
        sizer.Add(self._brw_jar, 0, wx.GROW)

        # Bind
        self.Bind(EVT_BROWSE, self.OnBrowse, self._brw_java)
        self.Bind(EVT_BROWSE, self.OnBrowse, self._brw_jar)

        # Values
        if 'nistmonte' in settings:
            path = getattr(settings.nistmonte, 'java', None)
            try:
                self._brw_java.SetPath(path)
            except ValueError:
                pass

            path = getattr(settings.nistmonte, 'jar', None)
            try:
                self._brw_jar.SetPath(path)
            except ValueError:
                pass

    def OnBrowse(self, event):
        self._brw_java.SetBaseDir(event.path)
        self._brw_jar.SetBaseDir(event.path)

    def Validate(self):
        if not ConfigurePanel.Validate(self):
            return False

        if not self._brw_java.GetPath():
            show_error_dialog(self, 'Please specify the Java executable')
            return False

        if not self._brw_jar.GetPath():
            show_error_dialog(self, 'Please specify the pymontecarlo-nistmonte jar')
            return False

        return True

    def save(self, settings):
        section = settings.add_section('nistmonte')
        section.java = self._brw_java.GetPath()
        section.jar = self._brw_jar.GetPath()

class _NistMonteGUI(GUI):

    def create_configure_panel(self, parent, settings):
        """
        Returns the configure panel for this program.
        
        :arg parent: parent window
        :arg settings: settings object
        """
        return _NistMonteConfigurePanel(parent, program, settings)

gui = _NistMonteGUI()

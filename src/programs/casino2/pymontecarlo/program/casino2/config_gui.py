#!/usr/bin/env python
"""
================================================================================
:mod:`config_gui` -- Casino 2 Monte Carlo program GUI configuration
================================================================================

.. module:: config_gui
   :synopsis: Casino 2 Monte Carlo program GUI configuration

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

# Local modules.
from pymontecarlo.program.config_gui import GUI, _ConfigurePanelWidget
from pymontecarlo.program.casino2.config import program

from pymontecarlo.ui.gui.util.widget import FileBrowseWidget

# Globals and constants variables.

class _Casino2ConfigurePanelWidget(_ConfigurePanelWidget):

    def _initUI(self, settings):
        # Widgets
        self._brw_exe = FileBrowseWidget()
        self._brw_exe.setNameFilter('Application files (*.exe)')

        # Layouts
        layout = _ConfigurePanelWidget._initUI(self, settings)
        layout.addRow('Full path to WinCasino.exe', self._brw_exe)

        # Defaults
        if 'casino2' in settings:
            path = getattr(settings.casino2, 'exe', None)
            try:
                self._brw_exe.setPath(path)
            except ValueError:
                pass

        return layout

    def hasAcceptableInput(self):
        if not self._brw_exe.path():
            return False
        if not os.access(self._brw_exe.path(), os.X_OK):
            return False
        return True

    def updateSettings(self, settings):
        section = _ConfigurePanelWidget.updateSettings(self, settings)
        section.exe = self._brw_exe.path()
        return section

class _Casino2GUI(GUI):

    def create_configure_panel(self, parent=None):
        return _Casino2ConfigurePanelWidget(program, parent)

gui = _Casino2GUI()

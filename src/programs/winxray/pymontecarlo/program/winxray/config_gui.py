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
import os

# Third party modules.

# Local modules.
from pymontecarlo.program.config_gui import GUI, _ConfigurePanelWidget
from pymontecarlo.program.winxray.config import program

from pymontecarlo.ui.gui.util.widget import FileBrowseWidget

# Globals and constants variables.

class _WinXRayConfigurePanelWidget(_ConfigurePanelWidget):

    def _initUI(self, settings):
        # Widgets
        self._brw_exe = FileBrowseWidget()
        self._brw_exe.setNameFilter('Application files (*.exe)')

        # Layouts
        layout = _ConfigurePanelWidget._initUI(self, settings)
        layout.addRow('Full path to WinXRay.exe', self._brw_exe)

        # Values
        if 'winxray' in settings:
            path = getattr(settings.winxray, 'exe', None)
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
        section.exe = self._brw_exe.GetPath()
        return section

class _WinXRayGUI(GUI):

    def create_configure_panel(self, parent=None):
        """
        Returns the configure panel for this program.

        :arg parent: parent window
        :arg settings: settings object
        """
        return _WinXRayConfigurePanelWidget(program, parent)

gui = _WinXRayGUI()

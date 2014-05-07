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

# Local modules.
from pymontecarlo.program.config_gui import GUI, _ConfigurePanelWidget
from pymontecarlo.program.monaco.config import program

from pymontecarlo.ui.gui.util.widget import DirBrowseWidget

# Globals and constants variables.

class _MonacoConfigurePanelWidget(_ConfigurePanelWidget):

    def _initUI(self, settings):
        # Widgets
        self._brw_basedir = DirBrowseWidget()

        # Layouts
        layout = _ConfigurePanelWidget._initUI(self, settings)
        layout.addRow('Full path to base directory', self._brw_basedir)

        # Values
        if 'monaco' in settings:
            path = getattr(settings.monaco, 'basedir', None)
            try:
                self._brw_basedir.setPath(path)
            except ValueError:
                pass

        return layout

    def hasAcceptableInput(self):
        basedir = self._brw_basedir.path()
        if not basedir:
            return False

        mccli32_exe = os.path.join(basedir, 'Mccli32.exe')
        if not os.path.isfile(mccli32_exe):
            return False

        return True

    def updateSettings(self, settings):
        section = _ConfigurePanelWidget.updateSettings(self, settings)
        section.basedir = self._brw_basedir.GetPath()
        return section

class _MonacoGUI(GUI):

    def create_configure_panel(self, parent=None):
        """
        Returns the configure panel for this program.

        :arg parent: parent window
        :arg settings: settings object
        """
        return _MonacoConfigurePanelWidget(program, parent)

gui = _MonacoGUI()

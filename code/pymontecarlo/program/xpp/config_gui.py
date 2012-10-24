#!/usr/bin/env python
"""
================================================================================
:mod:`config_gui` -- XPP Monte Carlo program GUI configuration
================================================================================

.. module:: config_gui
   :synopsis: XPP Monte Carlo program GUI configuration

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.program.config_gui import GUI, ConfigurePanel
from pymontecarlo.program.xpp.config import program

# Globals and constants variables.

class _XPPGUI(GUI):

    def create_configure_panel(self, parent, settings):
        """
        Returns the configure panel for this program.
        
        :arg parent: parent window
        :arg settings: settings object
        """
        return ConfigurePanel(parent, program, settings)

gui = _XPPGUI()

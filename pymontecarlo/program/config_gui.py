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
from PySide.QtGui import QWidget, QLabel, QFormLayout, QVBoxLayout

# Local modules.

# Globals and constants variables.

class _ConfigurePanelWidget(QWidget):

    def __init__(self, program, parent=None):
        QWidget.__init__(self, parent)

        # Variables
        self._program = program

        # Controls
        lbl_program = QLabel(program.name)
        font = lbl_program.font()
        font.setBold(True)
        font.setPointSize(14)
        lbl_program.setFont(font)

        # Sizer
        layout = QVBoxLayout()
        layout.addWidget(lbl_program)
        layout.addLayout(self._initUI())
        layout.addStretch()
        self.setLayout(layout)

    def _initUI(self):
        return QFormLayout()

    def program(self):
        return self._program

    def hasAcceptableInput(self):
        return True

    def setSettings(self, settings):
        pass

    def updateSettings(self, settings):
        """
        Update the settings from the information inside the widget
        """
        return settings.add_section(self.program().alias)

class GUI(object):

    def create_configure_panel(self, parent=None):
        """
        Returns the configure panel for this program.

        :arg parent: parent window
        :arg settings: settings object
        """
        raise NotImplementedError

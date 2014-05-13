#!/usr/bin/env python
"""
================================================================================
:mod:`name` -- Name wizard page
================================================================================

.. module:: name
   :synopsis: Name wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.name

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from PySide.QtGui import QLineEdit, QRegExpValidator
from PySide.QtCore import QRegExp

# Local modules.
from pymontecarlo.ui.gui.options.wizard.options import _OptionsWizardPage

# Globals and constants variables.

class NameWizardPage(_OptionsWizardPage):

    def __init__(self, options, parent=None):
        _OptionsWizardPage.__init__(self, options, parent)
        self.setTitle("Name")

    def _initUI(self):
        # Widgets
        self._txt_name = QLineEdit()
        self._txt_name.setValidator(QRegExpValidator(QRegExp(r"^(?!\s*$).+")))

        # Layouts
        layout = _OptionsWizardPage._initUI(self)
        layout.addRow('Name', self._txt_name)

        # Signals
        self._txt_name.textChanged.connect(self._onNameChanged)

        return layout

    def _onNameChanged(self):
        if self._txt_name.hasAcceptableInput():
            self._txt_name.setStyleSheet("background: none")
        else:
            self._txt_name.setStyleSheet("background: pink")

    def initializePage(self):
        name = self.options().name
        self._txt_name.setText(name)

    def validatePage(self):
        if not self._txt_name.hasAcceptableInput():
            return False

        self.options().name = self._txt_name.text()
        return True

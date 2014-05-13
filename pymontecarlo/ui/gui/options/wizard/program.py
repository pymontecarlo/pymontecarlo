#!/usr/bin/env python
"""
================================================================================
:mod:`program` -- Program wizard page
================================================================================

.. module:: program
   :synopsis: Program wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.program

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import methodcaller, attrgetter

# Third party modules.
from PySide.QtGui import \
    QCheckBox, QPushButton, QSizePolicy, QSpacerItem, QHBoxLayout

# Local modules.
from pymontecarlo.ui.gui.options.wizard.options import _OptionsWizardPage

from pymontecarlo.settings import get_settings

# Globals and constants variables.

class ProgramWizardPage(_OptionsWizardPage):

    def __init__(self, options, parent=None):
        _OptionsWizardPage.__init__(self, options, parent)
        self.setTitle("Program")

    def _initUI(self):
        # Variable
        settings = get_settings()

        # Widgets
        self._checkboxes = {}
        for program in settings.get_programs():
            self._checkboxes[program] = QCheckBox(program.name)

        btn_selectall = QPushButton('Select all')
        btn_deselectall = QPushButton('Deselect all')

        # Layouts
        layout = _OptionsWizardPage._initUI(self)
        for program in sorted(self._checkboxes.keys() , key=attrgetter('name')):
            layout.addRow(self._checkboxes[program])

        spacer = QSpacerItem(0, 1000, QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addItem(spacer)

        sublayout = QHBoxLayout()
        sublayout.addWidget(btn_selectall)
        sublayout.addWidget(btn_deselectall)
        layout.addRow(sublayout)

        # Signals
        btn_selectall.released.connect(self._onSelectAll)
        btn_deselectall.released.connect(self._onDeselectAll)

        return layout

    def _onSelectAll(self):
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(True)

    def _onDeselectAll(self):
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(False)

    def initializePage(self):
        programs = self.options().programs
        for program, checkbox in self._checkboxes.items():
            checkbox.setChecked(program in programs)

    def validatePage(self):
        if not any(map(methodcaller('isChecked'), self._checkboxes.values())):
            return False

        self.options().programs.clear()
        for program, checkbox in self._checkboxes.items():
            if checkbox.isChecked():
                self.options().programs.add(program)

        return True

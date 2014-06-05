#!/usr/bin/env python
"""
================================================================================
:mod:`configure` -- Configure dialog
================================================================================

.. module:: configure
   :synopsis: Configure dialog

.. inheritance-diagram:: pymontecarlo.ui.gui.configure

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
from operator import attrgetter

# Third party modules.
from PySide.QtGui import \
    (QDialog, QDialogButtonBox, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
     QPushButton, QListView, QStackedWidget, QWidget, QMessageBox, QFileDialog)
from PySide.QtCore import Qt, QAbstractListModel

# Local modules.
from pymontecarlo.settings import get_settings

# Globals and constants variables.

class _ProgramListModel(QAbstractListModel):

    def __init__(self, programs=None):
        QAbstractListModel.__init__(self)
        self._programs = programs or []

    def rowCount(self, *args, **kwargs):
        return len(self._programs)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._programs)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        return self._programs[index.row()].name

    def add(self, program):
        self._programs.append(program)
        self.reset()

    def remove(self, program):
        self._programs.remove(program)
        self.reset()

    def program(self, index):
        return self._programs[index]

    def programs(self):
        return list(self._programs)

class ConfigureDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Configuration")

        # Variables
        settings = get_settings()

        self._widgets = {}
        for program in settings.get_available_programs():
            try:
                gui = settings.get_program_gui(program)
            except:
                continue
            self._widgets[program] = gui.create_configure_panel()

        available_programs = sorted(self._widgets.keys(), key=attrgetter('name'))

        # Controls
        self._cb_available_programs = QComboBox()
        model = _ProgramListModel(available_programs)
        self._cb_available_programs.setModel(model)

        self._btn_activate = QPushButton('Activate')

        self._lst_selected_programs = QListView()
        model = _ProgramListModel()
        self._lst_selected_programs.setModel(model)
        self._lst_selected_programs.setMaximumWidth(150)

        self._wdg_program = QStackedWidget()
        self._wdg_program.addWidget(QWidget())
        for program in available_programs:
            self._wdg_program.addWidget(self._widgets[program])

        self._btn_deactivate = QPushButton('Deactivate')

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        btnauto = QPushButton('Auto')
        buttons.addButton(btnauto, QDialogButtonBox.ActionRole)

        # Layouts
        layout = QVBoxLayout()

        sublayout = QHBoxLayout()
        sublayout.addWidget(QLabel('Available programs'))
        sublayout.addWidget(self._cb_available_programs, 1)
        sublayout.addWidget(self._btn_activate)
        layout.addLayout(sublayout)

        sublayout = QHBoxLayout()

        subsublayout = QVBoxLayout()
        subsublayout.addWidget(self._lst_selected_programs)
        subsublayout.addWidget(self._btn_deactivate)
        sublayout.addLayout(subsublayout)

        sublayout.addWidget(self._wdg_program, 1)

        layout.addLayout(sublayout, 1)

        layout.addWidget(buttons)

        self.setLayout(layout)

        # Signals
        self._lst_selected_programs.activated.connect(self._onSelectProgram)

        self._btn_activate.released.connect(self._onActivate)
        self._btn_deactivate.released.connect(self._onDeactivate)
        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self.reject)
        btnauto.released.connect(self._onAuto)

        # Defaults
        for program in settings.get_programs():
            self.activateProgram(program)

    def activateProgram(self, program):
        self._lst_selected_programs.model().add(program)

        self._cb_available_programs.model().remove(program)
        if self._cb_available_programs.currentIndex() < 0:
            self._cb_available_programs.setCurrentIndex(0)

        enabled = self._cb_available_programs.model().rowCount() != 0
        self._btn_activate.setEnabled(enabled)

        enabled = self._lst_selected_programs.model().rowCount() != 0
        self._btn_deactivate.setEnabled(enabled)

        index = self._lst_selected_programs.model().rowCount() - 1
        program = self._lst_selected_programs.model().program(index)
        widget = self._widgets[program]
        widget.setSettings(get_settings())
        self._wdg_program.setCurrentWidget(widget)

    def deactivateProgram(self, program):
        self._lst_selected_programs.model().remove(program)

        self._cb_available_programs.model().add(program)
        if self._cb_available_programs.currentIndex() < 0:
            self._cb_available_programs.setCurrentIndex(0)

        enabled = self._cb_available_programs.model().rowCount() != 0
        self._btn_activate.setEnabled(enabled)

        enabled = self._lst_selected_programs.model().rowCount() != 0
        self._btn_deactivate.setEnabled(enabled)

        self._wdg_program.setCurrentIndex(0)

    def _onActivate(self):
        index = self._cb_available_programs.currentIndex()
        try:
            program = self._cb_available_programs.model().program(index)
        except IndexError:
            return
        self.activateProgram(program)

    def _onDeactivate(self):
        selection = \
            self._lst_selected_programs.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Configuration", "Select a program")
            return

        model = self._lst_selected_programs.model()
        for index in selection:
            program = model.program(index.row())
            self.deactivateProgram(program)

    def _onSelectProgram(self, index):
        program = self._lst_selected_programs.model().program(index.row())
        widget = self._widgets[program]
        self._wdg_program.setCurrentWidget(widget)

    def _onOk(self):
        selected_programs = self._lst_selected_programs.model().programs()

        # Check for errors
        error_programs = []
        for program in selected_programs:
            widget = self._widgets[program]
            if not widget.hasAcceptableInput():
                error_programs.append(program)

        if error_programs:
            if len(error_programs) >= 2:
                message = 'The following programs contain error(s):\n'
                title = 'Validation errors'
            else:
                message = 'The following program contains error(s):\n'
                title = 'Validation error'

            for program in error_programs:
                message += '- %s\n' % program.name

            QMessageBox.critical(widget.parent(), title, message)
            return

        # Save settings
        settings = get_settings()

        for program in selected_programs:
            widget = self._widgets[program]
            widget.updateSettings(settings)

        settings.pymontecarlo.programs = \
            ','.join(map(attrgetter('alias'), selected_programs))

        # Save settings
        settings.write()
        QMessageBox.information(self, 'Configuration', 'Saved')

        self.accept()

    def _onAuto(self):
        settings = get_settings()
        programs = set(settings.get_available_programs())
        programs -= set(self._lst_selected_programs.model().programs())
        if not programs:
            return

        # Ask for program path
        if sys.platform != 'linux':
            basedir = os.path.join(os.path.dirname(sys.executable), 'programs')
            programs_path = \
                QFileDialog.getExistingDirectory(self, "Browse directory", basedir)
        else:
            programs_path = None

        for program in programs:
            if program.autoconfig(programs_path):
                self.activateProgram(program)

def __run():
    from PySide.QtGui import QApplication

    app = QApplication(sys.argv)

    dialog = ConfigureDialog()
    dialog.exec_()

    app.exec_()

if __name__ == '__main__':
    __run()

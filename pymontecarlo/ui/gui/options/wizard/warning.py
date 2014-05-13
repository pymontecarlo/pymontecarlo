#!/usr/bin/env python
"""
================================================================================
:mod:`warning` -- Warning wizard page
================================================================================

.. module:: warning
   :synopsis: Warning wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.warning

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings

# Third party modules.
from PySide.QtGui import QTableView, QHeaderView, QFrame, QHBoxLayout
from PySide.QtCore import Qt, QAbstractTableModel

# Local modules.
from pymontecarlo.ui.gui.options.wizard.options import \
    _OptionsWizardPage, SimulationCountLabel

# Globals and constants variables.

class WarningWizardPage(_OptionsWizardPage):

    class _WarningTableModel(QAbstractTableModel):

        def __init__(self, warns=None):
            QAbstractTableModel.__init__(self)
            if warns is None:
                warns = []
            self._warns = warns

        def rowCount(self, *args, **kwargs):
            return len(self._warns)

        def columnCount(self, *args, **kwargs):
            return 2

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._warns)):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            return str(self._warns[index.row()][index.column()])

        def headerData(self, section , orientation, role):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Horizontal:
                if section == 0:
                    return 'Program'
                elif section == 1:
                    return 'Warning'
            elif orientation == Qt.Vertical:
                return str(section + 1)

        def flags(self, index):
            if not index.isValid():
                return Qt.ItemIsEnabled

            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))

    def __init__(self, options, parent=None):
        _OptionsWizardPage.__init__(self, options, parent=parent)
        self.setTitle("Conversion warnings")

        # Widgets
        self._lbl_count = SimulationCountLabel()
        self._lbl_count.setAlignment(Qt.AlignCenter)

        # Layouts
        layout = self.layout()

        frm_line = QFrame()
        frm_line.setFrameStyle(QFrame.HLine)
        frm_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(frm_line)

        sublayout = QHBoxLayout()
        sublayout.setContentsMargins(10, 0, 10, 0)
        sublayout.addWidget(self._lbl_count)
        layout.addLayout(sublayout)

    def _initUI(self):
        # Widgets
        self._tbl_warnings = QTableView()
        self._tbl_warnings.setModel(self._WarningTableModel())
        header = self._tbl_warnings.horizontalHeader()
        header.setResizeMode(1, QHeaderView.Stretch)
        policy = self._tbl_warnings.sizePolicy()
        policy.setVerticalStretch(True)
        self._tbl_warnings.setSizePolicy(policy)

        # Layouts
        layout = _OptionsWizardPage._initUI(self)
        layout.addRow(self._tbl_warnings)

        return layout

    def initializePage(self):
        count = 0
        warns = []

        for program in self.options().programs:
            converter = program.converter_class()

            warnings.simplefilter("always")
            with warnings.catch_warnings(record=True) as ws:
                list_options = converter.convert(self.options())
                count += len(list_options)

            for w in ws:
                warns.append((program, w.message))

        model = self._WarningTableModel(warns)
        self._tbl_warnings.setModel(model)

        self._lbl_count.setValue(count)

    def validatePage(self):
        return self._lbl_count.value() > 0

#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- Detector wizard page
================================================================================

.. module:: detector
   :synopsis: Detector wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.detector

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter, methodcaller

# Third party modules.
from PySide.QtGui import \
    (QHBoxLayout, QComboBox, QTableView, QToolBar, QPushButton, QItemDelegate,
     QLineEdit, QRegExpValidator, QWidget, QSizePolicy, QMessageBox,
     QHeaderView, QDialog, QFormLayout, QDialogButtonBox)
from PySide.QtCore import \
    Qt, QAbstractTableModel, QModelIndex, QRegExp, QAbstractListModel

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.tango import getIcon
from pymontecarlo.ui.gui.options.wizard.options import \
    _ExpandableOptionsWizardPage

from pymontecarlo.util.parameter import expand

# Globals and constants variables.

#--- Wizard page

class _DetectorDialog(QDialog):

    def __init__(self, wdg_detector, key='', parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(wdg_detector.accessibleName())

        # Widgets
        self._txt_key = QLineEdit()
        self._txt_key.setValidator(QRegExpValidator(QRegExp(r"^(?!\s*$).+")))
        self._txt_key.setText(key)

        self._wdg_detector = wdg_detector

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layouts
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow) # Fix for Mac OS
        layout.addRow('Key', self._txt_key)
        layout.addRow(self._wdg_detector)
        layout.addRow(buttons)
        self.setLayout(layout)

        # Signals
        self._txt_key.textChanged.connect(self._onChanged)
        self._txt_key.textChanged.emit('')

        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self.reject)

    def _onChanged(self):
        if self._txt_key.hasAcceptableInput():
            self._txt_key.setStyleSheet("background: none")
        else:
            self._txt_key.setStyleSheet("background: pink")

    def _onOk(self):
        if not self._txt_key.hasAcceptableInput():
            return
        if not self._wdg_detector.hasAcceptableInput():
            return
        self.accept()

    def key(self):
        return self._txt_key.text()

    def detector(self):
        return self._wdg_detector.value()

class DetectorWizardPage(_ExpandableOptionsWizardPage):

    class _DetectorComboBoxModel(QAbstractListModel):

        def __init__(self):
            QAbstractListModel.__init__(self)
            self._detectors = []

        def rowCount(self, *args, **kwargs):
            return len(self._detectors)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < self.rowCount()):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            return self._detectors[index.row()]['text']

        def setData(self, index, value, role=Qt.EditRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._detectors)):
                return False

            row = index.row()
            self._detectors[row] = value

            self.dataChanged.emit(index, index)
            return True

        def insertRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginInsertRows(QModelIndex(), row, row + count - 1)

            for _ in range(count):
                value = {'text': '', 'class': None, 'widget_class': None}
                self._detectors.insert(row, value)

            self.endInsertRows()
            return True

        def removeRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginRemoveRows(QModelIndex(), row, row + count - 1)

            for index in reversed(range(row, row + count)):
                self._detectors.pop(index)

            self.endRemoveRows()
            return True

        def append(self, text, clasz, widget_class):
            self.insert(self.rowCount(), text, clasz, widget_class)

        def insert(self, row, text, clasz, widget_class):
            self.insertRows(row)
            value = {'text': text, 'class': clasz, 'widget_class': widget_class}
            self.setData(self.createIndex(row, 0), value)

        def clear(self):
            self.removeRows(0, self.rowCount())

        def widget_class(self, index):
            return self._detectors[index]['widget_class']

    class _DetectorTableModel(QAbstractTableModel):

        def __init__(self):
            QAbstractTableModel.__init__(self)
            self._detectors = []

        def rowCount(self, *args, **kwargs):
            return len(self._detectors)

        def columnCount(self, *args, **kwargs):
            return 2

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._detectors)):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role == Qt.DisplayRole or role == Qt.ToolTipRole:
                key, detector = self._detectors[index.row()]
                column = index.column()
                if column == 0:
                    return key
                elif column == 1:
                    return str(detector) if detector is not None else ''

            return None

        def headerData(self, section , orientation, role):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Horizontal:
                if section == 0:
                    return 'Key'
                elif section == 1:
                    return 'Detector'
            elif orientation == Qt.Vertical:
                return str(section + 1)

        def flags(self, index):
            if not index.isValid():
                return Qt.ItemIsEnabled

            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                Qt.ItemIsEditable)

        def setData(self, index, value, role=Qt.EditRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._detectors)):
                return False

            row = index.row()
            column = index.column()
            self._detectors[row][column] = value

            self.dataChanged.emit(index, index)
            return True

        def insertRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginInsertRows(parent, row, row + count - 1)

            for _ in range(count):
                self._detectors.insert(row, ['untitled', None])

            self.endInsertRows()
            return True

        def removeRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginRemoveRows(parent, row, row + count - 1)

            for index in reversed(range(row, row + count)):
                self._detectors.pop(index)

            self.endRemoveRows()
            return True

        def append(self, key, detector):
            self.insert(self.rowCount(), key, detector)

        def insert(self, index, key, detector):
            self.insertRows(index)
            self.setData(self.createIndex(index, 0), key)
            self.setData(self.createIndex(index, 1), detector)

        def modify(self, index, key, detector):
            self.setData(self.createIndex(index, 0), key)
            self.setData(self.createIndex(index, 1), detector)

        def clear(self):
            self.removeRows(0, self.rowCount())

        def detectors(self):
            detectors = {}
            for key, detector in self._detectors:
                if detector is not None:
                    detectors.setdefault(key, []).append(detector)
            return detectors

        def detector(self, index):
            return self._detectors[index.row()][1]

        def key(self, index):
            return self._detectors[index.row()][0]

    class _DetectorTableDelegate(QItemDelegate):

        def __init__(self, parent=None):
            QItemDelegate.__init__(self, parent)

        def createEditor(self, parent, option, index):
            column = index.column()
            if column == 0:
                editor = QLineEdit(parent)
                editor.setValidator(QRegExpValidator(QRegExp(r"^(?!\s*$).+")))
                return editor
            elif column == 1:
                return None

        def setEditorData(self, editor, index):
            column = index.column()
            if column == 0:
                key = index.model().data(index, Qt.DisplayRole)
                editor.setText(key)

        def setModelData(self, editor, model, index):
            column = index.column()
            if column == 0:
                if not editor.hasAcceptableInput():
                    return
                model.setData(index, editor.text())

    def __init__(self, options, parent=None):
        _ExpandableOptionsWizardPage.__init__(self, options, parent)
        self.setTitle('Detector')

    def _initUI(self):
        # Variables
        self._widgets = {}
        tbl_model = self._DetectorTableModel()

        # Widgets
        self._cb_detector = QComboBox()
        self._cb_detector.setModel(self._DetectorComboBoxModel())

        btn_detector_add = QPushButton()
        btn_detector_add.setIcon(getIcon("list-add"))

        self._tbl_detector = QTableView()
        self._tbl_detector.setModel(tbl_model)
        self._tbl_detector.setItemDelegate(self._DetectorTableDelegate())
        header = self._tbl_detector.horizontalHeader()
        header.setResizeMode(1, QHeaderView.Stretch)
        policy = self._tbl_detector.sizePolicy()
        policy.setVerticalStretch(True)
        self._tbl_detector.setSizePolicy(policy)

        tlb_detector = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tlb_detector.addWidget(spacer)
        act_remove = tlb_detector.addAction(getIcon("list-remove"), "Remove detector")
        act_clear = tlb_detector.addAction(getIcon("edit-clear"), "Clear")

        # Layouts
        layout = _ExpandableOptionsWizardPage._initUI(self)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self._cb_detector, 1)
        sublayout.addWidget(btn_detector_add)
        layout.addRow("Select", sublayout)

        layout.addRow(self._tbl_detector)
        layout.addRow(tlb_detector)

        # Signals
        btn_detector_add.released.connect(self._onDetectorAdd)
        act_remove.triggered.connect(self._onDetectorRemove)
        act_clear.triggered.connect(self._onDetectorClear)

        self._tbl_detector.doubleClicked.connect(self._onDetectorDoubleClicked)

        tbl_model.dataChanged.connect(self.valueChanged)
        tbl_model.rowsInserted.connect(self.valueChanged)
        tbl_model.rowsRemoved.connect(self.valueChanged)

        return layout

    def _onDetectorAdd(self):
        index = self._tbl_detector.selectionModel().currentIndex()
        tbl_model = self._tbl_detector.model()
        cb_model = self._cb_detector.model()

        widget_class = cb_model.widget_class(self._cb_detector.currentIndex())
        wdg_detector = widget_class()

        dialog = _DetectorDialog(wdg_detector)
        if not dialog.exec_():
            return

        tbl_model.insert(index.row() + 1, dialog.key(), dialog.detector())

    def _onDetectorRemove(self):
        selection = self._tbl_detector.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Detector", "Select a row")
            return

        tbl_model = self._tbl_detector.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            tbl_model.removeRow(row)

    def _onDetectorClear(self):
        model = self._tbl_detector.model()
        for row in reversed(range(model.rowCount())):
            model.removeRow(row)

    def _onDetectorDoubleClicked(self, index):
        if index.column() != 1:
            return

        tbl_model = self._tbl_detector.model()
        key = tbl_model.key(index)
        detector = tbl_model.detector(index)
        widget_class = self._widgets[detector.__class__]
        wdg_detector = widget_class()
        wdg_detector.setValue(detector)

        dialog = _DetectorDialog(wdg_detector, key)
        if not dialog.exec_():
            return

        tbl_model.modify(index.row(), dialog.key(), dialog.detector())

    def initializePage(self):
        _ExpandableOptionsWizardPage.initializePage(self)

        tbl_model = self._tbl_detector.model()
        cb_model = self._cb_detector.model()

        # Clear
        self._widgets.clear()
        tbl_model.clear()
        cb_model.clear()

        # Populate combo box
        it = self._iter_widgets('pymontecarlo.ui.gui.options.detector',
                                'DETECTORS')
        for clasz, widget_class, programs in it:
            widget = widget_class()
            self._widgets[clasz] = widget_class

            program_text = ', '.join(map(attrgetter('name'), programs))
            text = '{0} ({1})'.format(widget.accessibleName(), program_text)

            cb_model.append(text, clasz, widget_class)

            del widget

        self._cb_detector.setCurrentIndex(0)

        # Add detector(s)
        for key, detectors in self.options().detectors.items():
            detectors = np.array(detectors, ndmin=1)
            for detector in detectors:
                if not detector.__class__ in self._widgets:
                    continue
                tbl_model.append(key, detector)

    def validatePage(self):
        tbl_model = self._tbl_detector.model()
        if tbl_model.rowCount() == 0:
            return False

        self.options().detectors.clear()
        self.options().detectors.update(tbl_model.detectors())

        return True

    def expandCount(self):
        if self._tbl_detector.model().rowCount() == 0:
            return 0

        try:
            count = 1

            for detectors in self._tbl_detector.model().detectors().values():
                count *= len(detectors)
                for detector in detectors:
                    count *= len(expand(detector))

            return count
        except:
            return 0


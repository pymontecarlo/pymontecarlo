#!/usr/bin/env python
"""
================================================================================
:mod:`limit` -- Limit wizard page
================================================================================

.. module:: limit
   :synopsis: Limit wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.limit

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
    (QDialog, QDialogButtonBox, QTableView, QToolBar, QPushButton, QComboBox,
     QFormLayout, QHeaderView, QWidget, QSizePolicy, QHBoxLayout, QMessageBox,
     QItemDelegate)
from PySide.QtCore import \
    Qt, QModelIndex, QAbstractTableModel, QAbstractListModel

# Local modules.
from pymontecarlo.ui.gui.util.tango import getIcon
from pymontecarlo.ui.gui.options.wizard.options import \
    _ExpandableOptionsWizardPage

from pymontecarlo.util.parameter import expand

# Globals and constants variables.

class _LimitDialog(QDialog):

    def __init__(self, wdg_limit, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(wdg_limit.accessibleName())

        # Widgets
        self._wdg_limit = wdg_limit

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layouts
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow) # Fix for Mac OS
        layout.addRow(self._wdg_limit)
        layout.addRow(buttons)
        self.setLayout(layout)

        # Signals
        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self.reject)

    def _onOk(self):
        if not self._wdg_limit.hasAcceptableInput():
            return
        self.accept()

    def limit(self):
        return self._wdg_limit.value()

class LimitWizardPage(_ExpandableOptionsWizardPage):

    class _LimitComboBoxModel(QAbstractListModel):

        def __init__(self, limits_text=None):
            QAbstractListModel.__init__(self)

            if limits_text is None:
                limits_text = {}
            self._limits_text = limits_text.copy()

            self._limits = list(limits_text.keys())

        def rowCount(self, *args, **kwargs):
            return len(self._limits)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < self.rowCount()):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            limit_class = self._limits[index.row()]
            return self._limits_text[limit_class]

        def add(self, limit_class):
            if limit_class not in self._limits_text:
                raise ValueError('No text defined for limit: %s' % limit_class)
            self._limits.append(limit_class)
            self.reset()

        def remove(self, limit_class):
            self._limits.remove(limit_class)
            self.reset()

        def limitClass(self, index):
            return self._limits[index]

    class _LimitTableModel(QAbstractTableModel):

        def __init__(self):
            QAbstractTableModel.__init__(self)
            self._limits = []

        def rowCount(self, *args, **kwargs):
            return len(self._limits)

        def columnCount(self, *args, **kwargs):
            return 1

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._limits)):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role == Qt.DisplayRole or role == Qt.ToolTipRole:
                limit = self._limits[index.row()]
                return str(limit) if limit is not None else ''

            return None

        def headerData(self, section , orientation, role):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Vertical:
                return str(section + 1)

        def flags(self, index):
            if not index.isValid():
                return Qt.ItemIsEnabled

            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                Qt.ItemIsEditable)

        def setData(self, index, value, role=Qt.EditRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._limits)):
                return False

            row = index.row()
            self._limits[row] = value

            self.dataChanged.emit(index, index)
            return True

        def insertRows(self, row, count=1, parent=None):
            if parent is None:
                parent = QModelIndex()
            self.beginInsertRows(parent, row, row + count - 1)

            for _ in range(count):
                self._limits.insert(row, None)

            self.endInsertRows()
            return True

        def removeRows(self, row, count=1, parent=None):
            if parent is None:
                parent = QModelIndex()
            self.beginRemoveRows(parent, row, row + count - 1)

            for index in reversed(range(row, row + count)):
                self._limits.pop(index)

            self.endRemoveRows()
            return True

        def append(self, limit):
            self.insert(self.rowCount(), limit)

        def insert(self, index, limit):
            self.insertRows(index)
            self.setData(self.createIndex(index, 0), limit)

        def remove(self, limit):
            index = self._limits.index(limit)
            self.removeRows(index)

        def modify(self, index, limit):
            self.setData(self.createIndex(index, 0), limit)

        def clear(self):
            self.removeRows(0, self.rowCount())

        def limits(self):
            limits = set(self._limits)
            limits.discard(None)
            return limits

        def limit(self, index):
            return self._limits[index.row()]

    class _LimitTableDelegate(QItemDelegate):

        def __init__(self, parent=None):
            QItemDelegate.__init__(self, parent)

        def createEditor(self, parent, option, index):
            return None

        def setEditorData(self, editor, index):
            pass

        def setModelData(self, editor, model, index):
            return None

    def __init__(self, options, parent=None):
        _ExpandableOptionsWizardPage.__init__(self, options, parent)
        self.setTitle('Limit')

    def _initUI(self):
        # Variables
        self._widgets = {}
        tbl_model = self._LimitTableModel()

        # Widgets
        self._cb_limit = QComboBox()
        self._cb_limit.setModel(self._LimitComboBoxModel())

        btn_limit_add = QPushButton()
        btn_limit_add.setIcon(getIcon("list-add"))

        self._tbl_limit = QTableView()
        self._tbl_limit.setModel(tbl_model)
        self._tbl_limit.setItemDelegate(self._LimitTableDelegate())
        header = self._tbl_limit.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        header.hide()
        policy = self._tbl_limit.sizePolicy()
        policy.setVerticalStretch(True)
        self._tbl_limit.setSizePolicy(policy)

        tlb_limit = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tlb_limit.addWidget(spacer)
        act_remove = tlb_limit.addAction(getIcon("list-remove"), "Remove limit")
        act_clear = tlb_limit.addAction(getIcon("edit-clear"), "Clear")

        # Layouts
        layout = _ExpandableOptionsWizardPage._initUI(self)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self._cb_limit, 1)
        sublayout.addWidget(btn_limit_add)
        layout.addRow("Select", sublayout)

        layout.addRow(self._tbl_limit)
        layout.addRow(tlb_limit)

        # Signals
        btn_limit_add.released.connect(self._onLimitAdd)
        act_remove.triggered.connect(self._onLimitRemove)
        act_clear.triggered.connect(self._onLimitClear)

        self._tbl_limit.doubleClicked.connect(self._onLimitDoubleClicked)

        tbl_model.dataChanged.connect(self.valueChanged)
        tbl_model.rowsInserted.connect(self.valueChanged)
        tbl_model.rowsRemoved.connect(self.valueChanged)

        return layout

    def _onLimitAdd(self):
        tbl_model = self._tbl_limit.model()
        cb_model = self._cb_limit.model()

        index = self._cb_limit.currentIndex()
        try:
            limit_class = cb_model.limitClass(index)
        except IndexError:
            return
        widget_class = self._widgets[limit_class]
        wdg_limit = widget_class()

        dialog = _LimitDialog(wdg_limit)
        if not dialog.exec_():
            return

        limit = dialog.limit()
        tbl_model.append(limit) # Insert table row
        cb_model.remove(limit.__class__) # Remove limit from combo box

    def _onLimitRemove(self):
        selection = self._tbl_limit.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Limit", "Select a row")
            return

        tbl_model = self._tbl_limit.model()
        cb_model = self._cb_limit.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            limit = tbl_model.limit(tbl_model.createIndex(row, 0))
            cb_model.add(limit.__class__) # Show limit to combo box
            tbl_model.removeRow(row) # Remove row

        if self._cb_limit.currentIndex() < 0:
            self._cb_limit.setCurrentIndex(0)

    def _onLimitClear(self):
        tbl_model = self._tbl_limit.model()
        cb_model = self._cb_limit.model()
        for row in reversed(range(tbl_model.rowCount())):
            limit = tbl_model.limit(tbl_model.createIndex(row, 0))
            cb_model.add(limit.__class__) # Show limit to combo box
            tbl_model.removeRow(row) # Remove row

        if self._cb_limit.currentIndex() < 0:
            self._cb_limit.setCurrentIndex(0)

    def _onLimitDoubleClicked(self, index):
        tbl_model = self._tbl_limit.model()
        limit = tbl_model.limit(index)
        widget_class = self._widgets[limit.__class__]
        wdg_limit = widget_class()
        wdg_limit.setValue(limit)

        dialog = _LimitDialog(wdg_limit)
        if not dialog.exec_():
            return

        tbl_model.modify(index.row(), dialog.limit())

    def initializePage(self):
        _ExpandableOptionsWizardPage.initializePage(self)

        # Clear
        self._widgets.clear()
        limits_text = {}

        # Populate combo box
        it = self._iter_widgets('pymontecarlo.ui.gui.options.limit', 'LIMITS')
        for limit_class, widget_class, programs in it:
            widget = widget_class()
            self._widgets[limit_class] = widget_class

            program_text = ', '.join(map(attrgetter('name'), programs))
            text = '{0} ({1})'.format(widget.accessibleName(), program_text)
            limits_text[limit_class] = text

            del widget

        cb_model = self._LimitComboBoxModel(limits_text)
        self._cb_limit.setModel(cb_model)
        self._cb_limit.setCurrentIndex(0)

        # Add limit(s)
        tbl_model = self._tbl_limit.model()
        tbl_model.clear()

        for limit in self.options().limits:
            tbl_model.append(limit)

    def validatePage(self):
        tbl_model = self._tbl_limit.model()

        self.options().limits.clear()
        for limit in tbl_model.limits():
            if not limit.__class__ in self._widgets:
                continue
            self.options().limits.add(limit)

        return True

    def expandCount(self):
        if self._tbl_limit.model().rowCount() == 0:
            return 0

        try:
            count = 1

            for limit in self._tbl_limit.model().limits():
                count *= len(expand(limit))

            return count
        except:
            return 0

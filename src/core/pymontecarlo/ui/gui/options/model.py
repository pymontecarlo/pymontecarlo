#!/usr/bin/env python
"""
================================================================================
:mod:`model` -- Model widgets
================================================================================

.. module:: model
   :synopsis: Model widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.options.model

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from PySide.QtGui import QWidget, QTableView, QHeaderView, QVBoxLayout
from PySide.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal

# Local modules.

# Globals and constants variables.

class ModelTableWidget(QWidget):

    dataChanged = Signal(QModelIndex, QModelIndex)

    class _ModelTableModel(QAbstractTableModel):

        def __init__(self):
            QAbstractTableModel.__init__(self)
            self._models = []

        def rowCount(self, *args, **kwargs):
            return len(self._models)

        def columnCount(self, *args, **kwargs):
            return 2

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._models)):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            model = self._models[index.row()]
            if model is None:
                return ''

            if role == Qt.DisplayRole or role == Qt.ToolTipRole:
                column = index.column()
                if column == 0:
                    return str(model.type)
                elif column == 1:
                    return str(model)

            return None

        def headerData(self, section , orientation, role):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Horizontal:
                if section == 0:
                    return 'Type'
                elif section == 1:
                    return 'Model'
            elif orientation == Qt.Vertical:
                return str(section + 1)

        def flags(self, index):
            if not index.isValid():
                return Qt.ItemIsEnabled

            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))

        def setData(self, index, value, role=Qt.EditRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._models)):
                return False

            row = index.row()
            self._models[row] = value

            self.dataChanged.emit(index, index)
            return True

        def insertRows(self, row, count=1, parent=None):
            if parent is None:
                parent = QModelIndex()
            self.beginInsertRows(parent, row, row + count - 1)

            for _ in range(count):
                self._models.insert(row, None)

            self.endInsertRows()
            return True

        def removeRows(self, row, count=1, parent=None):
            if parent is None:
                parent = QModelIndex()
            self.beginRemoveRows(parent, row, row + count - 1)

            for index in reversed(range(row, row + count)):
                self._models.pop(index)

            self.endRemoveRows()
            return True

        def append(self, model):
            self.insert(self.rowCount(), model)

        def insert(self, index, model):
            self.insertRows(index)
            self.setData(self.createIndex(index, 0), model)

        def remove(self, model):
            index = self._models.index(model)
            self.removeRows(index)

        def clear(self):
            self.removeRows(0, self.rowCount())

        def models(self):
            models = set(self._models)
            models.discard(None)
            return models

        def model(self, index):
            return self._models[index.row()]

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Variables
        model = self._ModelTableModel()

        # Widgets
        self._tbl_models = QTableView()
        self._tbl_models.setModel(model)
        header = self._tbl_models.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        policy = self._tbl_models.sizePolicy()
        policy.setVerticalStretch(True)
        self._tbl_models.setSizePolicy(policy)
        self._tbl_models.setSelectionMode(QTableView.SelectionMode.MultiSelection)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self._tbl_models)
        self.setLayout(layout)

        # Signals
        model.dataChanged.connect(self.dataChanged)

    def addModel(self, model):
        self._tbl_models.model().append(model)

    def addModels(self, models):
        for model in models:
            self.addModel(model)

    def removeModel(self, model):
        self._tbl_models.model().remove(model)

    def clear(self):
        self._tbl_models.model().clear()

    def models(self):
        return self._tbl_models.model().models()

    def currentModels(self):
        tbl_model = self._tbl_models.model()

        models = []
        for index in self._tbl_models.selectionModel().selection().indexes():
            models.append(tbl_model.model(index))

        return models


#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- Geometry widgets
================================================================================

.. module:: geometry
   :synopsis: Geometry widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.options.geometry

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter, methodcaller
from collections import namedtuple

# Third party modules.
from PySide.QtGui import \
    (QLabel, QItemDelegate, QAction, QTableView, QToolBar, QHeaderView, QWidget,
     QSizePolicy, QVBoxLayout, QMessageBox, QValidator, QHBoxLayout)
from PySide.QtCore import Qt, QAbstractTableModel, QModelIndex

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    (_ParameterizedClassWidget, _ParameterWidget, UnitParameterWidget,
     AngleParameterWidget)
from pymontecarlo.ui.gui.util.widget import \
    MultiNumericalLineEdit, NumericalValidator, UnitComboBox
from pymontecarlo.ui.gui.util.tango import getIcon
from pymontecarlo.ui.gui.util.registry import get_widget_class as _get_widget_class

from pymontecarlo.ui.gui.options.material import \
    (MaterialListWidget, MaterialListDialog,
     get_dialog_class as get_material_dialog_class)

from pymontecarlo.options.material import Material
from pymontecarlo.options.geometry import \
    (_Geometry, Substrate, _SubstrateBody, Inclusion, _InclusionBody,
     Sphere, _SphereBody, HorizontalLayers, _HorizontalSubstrateBody,
     VerticalLayers, _VerticalLeftSubstrateBody, _VerticalRightSubstrateBody)

# Globals and constants variables.

#--- Parameter widgets

TiltWidget = AngleParameterWidget
RotationWidget = AngleParameterWidget
DiameterWidget = UnitParameterWidget

_MockLayer = namedtuple("_MockLayer", ("material", "thickness_m"))

class _ThicknessValidator(NumericalValidator):

    def validate(self, values):
        for value in values:
            if value <= 0.0:
                return QValidator.Intermediate
        return QValidator.Acceptable

class _LayerModel(QAbstractTableModel):

    def __init__(self):
        QAbstractTableModel.__init__(self)
        self._layers = []

    def rowCount(self, *args, **kwargs):
        return len(self._layers)

    def columnCount(self, *args, **kwargs):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._layers)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()

        materials, thicknesses = self._layers[row]
        if column == 0:
            if not materials:
                return 'none'
            else:
                return ', '.join(map(attrgetter('name'), materials))
        elif column == 1:
            if thicknesses:
                return ', '.join(map(str, thicknesses))

    def headerData(self, section , orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'Material'
            elif section == 1:
                return 'Thickness'
        elif orientation == Qt.Vertical:
            return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                            Qt.ItemIsEditable)

    def setData(self, index, values, role=Qt.EditRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._layers)):
            return False

        values = np.array(values, ndmin=1)

        row = index.row()
        column = index.column()
        self._layers[row][column].clear()
        self._layers[row][column].extend(values)

        self.dataChanged.emit(index, index)
        return True

    def insertRows(self, row, count=1, parent=None):
        if parent is None:
            parent = QModelIndex()
        self.beginInsertRows(QModelIndex(), row, row + count - 1)

        for _ in range(count):
            self._layers.insert(row, ([], []))

        self.endInsertRows()
        return True

    def removeRows(self, row, count=1, parent=None):
        if parent is None:
            parent = QModelIndex()
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)

        for index in reversed(range(row, row + count)):
            self._layers.pop(index)

        self.endRemoveRows()
        return True

    def materials(self, index):
        return self._layers[index.row()][0]

    def thicknesses(self, index):
        return self._layers[index.row()][1]

    def layers(self):
        return list(self._layers)

class _LayerDelegate(QItemDelegate):

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        self._readonly = False

    def createEditor(self, parent, option, index):
        column = index.column()
        if column == 1:
            editor = MultiNumericalLineEdit(parent)
            editor.setStyleSheet("background: none")
            editor.setReadOnly(self.isReadOnly())
            editor.setValidator(_ThicknessValidator())
            return editor

    def setEditorData(self, editor, index):
        column = index.column()
        if column == 1:
            thicknesses = index.model().thicknesses(index)
            if thicknesses:
                editor.setValues(thicknesses)

    def setModelData(self, editor, model, index):
        column = index.column()
        if column == 1:
            if not editor.hasAcceptableInput():
                return
            try:
                values = editor.values()
            except:
                return
            model.setData(index, values)

    def setReadOnly(self, state):
        self._readonly = state

    def isReadOnly(self):
        return self._readonly

class LayerListWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Variables
        model = _LayerModel()
        self._material_class = Material

        # Actions
        act_add = QAction(getIcon("list-add"), "Add layer", self)
        act_remove = QAction(getIcon("list-remove"), "Remove layer", self)
        act_clean = QAction(getIcon('edit-clear'), "Clear", self)

        # Widgets
        self._cb_unit = UnitComboBox('m')
        self._cb_unit.setUnit('um')

        self._tbl_layers = QTableView()
        self._tbl_layers.setModel(model)
        self._tbl_layers.setItemDelegate(_LayerDelegate())
        header = self._tbl_layers.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        header.setStyleSheet('color: blue')

        self._tlb_layers = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tlb_layers.addWidget(spacer)
        self._tlb_layers.addAction(act_add)
        self._tlb_layers.addAction(act_remove)
        self._tlb_layers.addAction(act_clean)

        # Layouts
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        sublayout = QHBoxLayout()
        sublayout.addStretch()
        sublayout.addWidget(QLabel('Thickness unit'))
        sublayout.addWidget(self._cb_unit)
        layout.addLayout(sublayout)

        layout.addWidget(self._tbl_layers)
        layout.addWidget(self._tlb_layers)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        act_add.triggered.connect(self._onAdd)
        act_remove.triggered.connect(self._onRemove)
        act_clean.triggered.connect(self._onClear)

        self._tbl_layers.doubleClicked.connect(self._onDoubleClicked)

        model.dataChanged.connect(self.valuesChanged)
        model.rowsInserted.connect(self.valuesChanged)
        model.rowsRemoved.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._tbl_layers.setStyleSheet("background: none")
        else:
            self._tbl_layers.setStyleSheet("background: pink")

    def _onDoubleClicked(self, index):
        if index.column() != 0:
            return

        model = self._tbl_layers.model()
        materials = model.materials(index)

        if len(materials) == 0:
            dialog = get_material_dialog_class(self._material_class)()
        elif len(materials) == 1:
            dialog = get_material_dialog_class(self._material_class)()
            dialog.setValue(materials[0])
        else:
            dialog = MaterialListDialog()
            dialog.setMaterialClass(self._material_class)
            dialog.setValues(materials)

        dialog.setReadOnly(self.isReadOnly())

        if not dialog.exec_():
            return

        model.setData(index, dialog.values())

    def _onAdd(self):
        index = self._tbl_layers.selectionModel().currentIndex()
        model = self._tbl_layers.model()
        model.insertRows(index.row() + 1)

        # Show material dialog right away
        index = model.createIndex(index.row() + 1, 0)
        self._onDoubleClicked(index)

    def _onRemove(self):
        selection = self._tbl_layers.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Layer", "Select a row")
            return

        model = self._tbl_layers.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            model.removeRow(row)

    def _onClear(self):
        model = self._tbl_layers.model()
        for row in reversed(range(model.rowCount())):
            model.removeRow(row)

    def values(self):
        factor = self._cb_unit.factor()

        layers = []
        for material, thickness in self._tbl_layers.model().layers():
            if not material or not thickness:
                continue
            thickness_m = np.array(thickness, ndmin=1) * factor
            layers.append(_MockLayer(material, thickness_m))

        return layers

    def setValues(self, layers):
        layers = np.array(layers, ndmin=1)
        factor = self._cb_unit.factor()

        model = self._tbl_layers.model()
        model.removeRows(0, model.rowCount())
        model.insertRows(0, len(layers))

        for i, layer in enumerate(layers):
            model.setData(model.index(i, 0), layer.material)
            model.setData(model.index(i, 1), layer.thickness_m / factor)

    def isReadOnly(self):
        return not self._cb_unit.isEnabled() and \
            not self._tlb_layers.isVisible()

    def setReadOnly(self, state):
        self._cb_unit.setEnabled(not state)
        self._tlb_layers.setVisible(not state)

        style = 'color: none' if state else 'color: blue'
        self._tbl_layers.horizontalHeader().setStyleSheet(style)
        self._tbl_layers.itemDelegate().setReadOnly(state)

    def setMaterialClass(self, clasz):
        self._material_class = clasz

#--- Geometry widgets

class _GeometryWidget(_ParameterizedClassWidget):

    def _initUI(self):
        # Widgets
        self._lbl_tilt = QLabel('Tilt')
        self._lbl_tilt.setStyleSheet('color: blue')
        self._txt_tilt = TiltWidget(_Geometry.tilt_rad)

        self._lbl_rotation = QLabel('Rotation')
        self._lbl_rotation.setStyleSheet('color: blue')
        self._txt_rotation = RotationWidget(_Geometry.rotation_rad)

        # Layouts
        layout = _ParameterizedClassWidget._initUI(self)
        layout.addRow(self._lbl_tilt, self._txt_tilt)
        layout.addRow(self._lbl_rotation, self._txt_rotation)

        return layout

    def setValue(self, geometry):
        self._txt_tilt.setValues(geometry.tilt_rad)
        self._txt_rotation.setValues(geometry.rotation_rad)

    def setReadOnly(self, state):
        _ParameterizedClassWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_tilt.setStyleSheet(style)
        self._lbl_rotation.setStyleSheet(style)

    def setMaterialClass(self, clasz):
        raise NotImplementedError

class SubstrateWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName('Substrate')

    def _initUI(self):
        # Widgets
        self._lbl_material = QLabel('Material')
        self._lbl_material.setStyleSheet('color: blue')
        self._lst_material = MaterialListWidget(_SubstrateBody.material)

        # Layouts
        layout = _GeometryWidget._initUI(self)
        layout.insertRow(0, self._lbl_material)
        layout.insertRow(1, self._lst_material)

        return layout

    def value(self):
        return Substrate(material=self._lst_material.values(),
                         tilt_rad=self._txt_tilt.values(),
                         rotation_rad=self._txt_rotation.values())

    def setValue(self, geometry):
        _GeometryWidget.setValue(self, geometry)
        if hasattr(geometry, 'body') and hasattr(geometry.body, 'material'):
            self._lst_material.setValues(geometry.body.material)

    def setReadOnly(self, state):
        _GeometryWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_material.setStyleSheet(style)

    def setMaterialClass(self, clasz):
        self._lst_material.setMaterialClass(clasz)

class InclusionWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Inclusion")

    def _initUI(self):
        # Widgets
        self._lbl_substrate = QLabel('Substrate')
        self._lbl_substrate.setStyleSheet('color: blue')
        self._lst_substrate = MaterialListWidget(_SubstrateBody.material)

        self._lbl_inclusion = QLabel('Inclusion')
        self._lbl_inclusion.setStyleSheet('color: blue')
        self._lst_inclusion = MaterialListWidget(_InclusionBody.material)

        self._lbl_diameter = QLabel('Inclusion diameter')
        self._lbl_diameter.setStyleSheet('color: blue')
        self._txt_diameter = DiameterWidget(_InclusionBody.diameter_m)

        # Layouts
        layout = _GeometryWidget._initUI(self)
        layout.insertRow(0, self._lbl_substrate)
        layout.insertRow(1, self._lst_substrate)
        layout.insertRow(2, self._lbl_inclusion)
        layout.insertRow(3, self._lst_inclusion)
        layout.insertRow(4, self._lbl_diameter, self._txt_diameter)

        return layout

    def value(self):
        return Inclusion(substrate_material=self._lst_substrate.values(),
                         inclusion_material=self._lst_inclusion.values(),
                         inclusion_diameter_m=self._txt_diameter.values(),
                         tilt_rad=self._txt_tilt.values(),
                         rotation_rad=self._txt_rotation.values())

    def setValue(self, geometry):
        _GeometryWidget.setValue(self, geometry)
        if hasattr(geometry, 'substrate') and \
                hasattr(geometry.substrate, 'material'):
            self._lst_substrate.setValues(geometry.substrate.material)
        if hasattr(geometry, 'inclusion') and \
                hasattr(geometry.inclusion, 'material'):
            self._lst_inclusion.setValues(geometry.inclusion.material)
        if hasattr(geometry, 'inclusion') and \
                hasattr(geometry.inclusion, 'diameter_m'):
            self._txt_diameter.setValues(geometry.inclusion.diameter_m)

    def setReadOnly(self, state):
        _GeometryWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_substrate.setStyleSheet(style)
        self._lbl_inclusion.setStyleSheet(style)
        self._lbl_diameter.setStyleSheet(style)

    def setMaterialClass(self, clasz):
        self._lst_substrate.setMaterialClass(clasz)
        self._lst_inclusion.setMaterialClass(clasz)

class HorizontalLayersWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Horizontal layers")

    def _initUI(self):
        # Widgets
        self._lbl_layer = QLabel('Layer')
        self._lbl_layer.setStyleSheet('color: blue')
        self._lst_layer = LayerListWidget(HorizontalLayers.layers)

        self._lbl_substrate = QLabel("Substrate (optional)")
        self._lbl_substrate.setStyleSheet('color: blue')
        self._lst_substrate = MaterialListWidget(_HorizontalSubstrateBody.material)
        self._lst_substrate.setRequired(False)

        # Layouts
        layout = _GeometryWidget._initUI(self)
        layout.insertRow(0, self._lbl_layer)
        layout.insertRow(1, self._lst_layer)
        layout.insertRow(2, self._lbl_substrate)
        layout.insertRow(3, self._lst_substrate)

        return layout

    def value(self):
        geometry = \
            HorizontalLayers(substrate_material=self._lst_substrate.values(),
                             tilt_rad=self._txt_tilt.values(),
                             rotation_rad=self._txt_rotation.values())

        for layer in self._lst_layer.values():
            geometry.add_layer(layer.material, layer.thickness_m)

        return geometry

    def setValue(self, geometry):
        _GeometryWidget.setValue(self, geometry)
        if hasattr(geometry, 'substrate') and \
                hasattr(geometry.substrate, 'material'):
            self._lst_substrate.setValues(geometry.substrate.material)
        if hasattr(geometry, 'layers'):
            self._lst_layer.setValues(geometry.layers)

    def setReadOnly(self, state):
        _GeometryWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_layer.setStyleSheet(style)
        self._lbl_substrate.setStyleSheet(style)

    def setMaterialClass(self, clasz):
        self._lst_layer.setMaterialClass(clasz)
        self._lst_substrate.setMaterialClass(clasz)

class VerticalLayersWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Vertical layers")

    def _initUI(self):
        # Widgets
        self._lbl_left = QLabel('Left substrate')
        self._lbl_left.setStyleSheet('color: blue')
        self._lst_left = MaterialListWidget(_VerticalLeftSubstrateBody.material)

        self._lbl_layer = QLabel('Layer')
        self._lbl_layer.setStyleSheet('color: blue')
        self._lst_layer = LayerListWidget(VerticalLayers.layers)
        self._lst_layer.setRequired(False)

        self._lbl_right = QLabel('Right substrate')
        self._lbl_right.setStyleSheet('color: blue')
        self._lst_right = MaterialListWidget(_VerticalRightSubstrateBody.material)

        self._lbl_depth = QLabel('Depth')
        self._lbl_depth.setStyleSheet('color: blue')
        self._txt_depth = UnitParameterWidget(VerticalLayers.depth_m)
        self._txt_depth.setValues(['inf'])

        # Layouts
        layout = _GeometryWidget._initUI(self)

        sublayout = QHBoxLayout()

        subsublayout = QVBoxLayout()
        subsublayout.addWidget(self._lbl_left)
        subsublayout.addWidget(self._lst_left)
        sublayout.addLayout(subsublayout)

        subsublayout = QVBoxLayout()
        subsublayout.addWidget(self._lbl_layer)
        subsublayout.addWidget(self._lst_layer)
        sublayout.addLayout(subsublayout)

        subsublayout = QVBoxLayout()
        subsublayout.addWidget(self._lbl_right)
        subsublayout.addWidget(self._lst_right)
        sublayout.addLayout(subsublayout)

        layout.insertRow(0, sublayout)
        layout.insertRow(1, self._lbl_depth, self._txt_depth)

        return layout

    def value(self):
        geometry = VerticalLayers(left_material=self._lst_left.values(),
                                  right_material=self._lst_right.values(),
                                  depth_m=self._txt_depth.values(),
                                  tilt_rad=self._txt_tilt.values(),
                                  rotation_rad=self._txt_rotation.values())

        for layer in self._lst_layer.values():
            geometry.add_layer(layer.material, layer.thickness_m)

        return geometry

    def setValue(self, geometry):
        _GeometryWidget.setValue(self, geometry)
        if hasattr(geometry, 'left_substrate') and \
                hasattr(geometry.left_substrate, 'material'):
            self._lst_left.setValues(geometry.left_substrate.material)
        if hasattr(geometry, 'layers'):
            self._lst_layer.setValues(geometry.layers)
        if hasattr(geometry, 'right_substrate') and \
                hasattr(geometry.right_substrate, 'material'):
            self._lst_right.setValues(geometry.right_substrate.material)
        if hasattr(geometry, 'depth_m'):
            self._txt_depth.setValues(geometry.depth_m)

    def setReadOnly(self, state):
        _GeometryWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_left.setStyleSheet(style)
        self._lbl_layer.setStyleSheet(style)
        self._lbl_right.setStyleSheet(style)
        self._lbl_depth.setStyleSheet(style)

    def setMaterialClass(self, clasz):
        self._lst_left.setMaterialClass(clasz)
        self._lst_layer.setMaterialClass(clasz)
        self._lst_right.setMaterialClass(clasz)

class SphereWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Sphere")

    def _initUI(self):
        # Widgets
        self._lbl_material = QLabel('Material')
        self._lbl_material.setStyleSheet('color: blue')
        self._lst_material = MaterialListWidget(_SphereBody.material)

        self._lbl_diameter = QLabel('Diameter')
        self._lbl_diameter.setStyleSheet('color: blue')
        self._txt_diameter = DiameterWidget(_SphereBody.diameter_m)

        # Layouts
        layout = _GeometryWidget._initUI(self)
        layout.insertRow(0, self._lbl_material)
        layout.insertRow(1, self._lst_material)
        layout.insertRow(2, self._lbl_diameter, self._txt_diameter)

        return layout

    def value(self):
        return Sphere(material=self._lst_material.values(),
                      diameter_m=self._txt_diameter.values(),
                      tilt_rad=self._txt_tilt.values(),
                      rotation_rad=self._txt_rotation.values())

    def setValue(self, geometry):
        _GeometryWidget.setValue(self, geometry)
        if hasattr(geometry, 'body') and hasattr(geometry.body, 'material'):
            self._lst_material.setValues(geometry.body.material)
        if hasattr(geometry, 'body') and hasattr(geometry.body, 'diameter_m'):
            self._txt_diameter.setValues(geometry.body.diameter_m)

    def setReadOnly(self, state):
        _GeometryWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_material.setStyleSheet(style)
        self._lbl_diameter.setStyleSheet(style)

    def setMaterialClass(self, clasz):
        self._lst_material.setMaterialClass(clasz)

#--- Functions

def get_widget_class(clasz):
    return _get_widget_class('pymontecarlo.ui.gui.options.geometry', clasz)


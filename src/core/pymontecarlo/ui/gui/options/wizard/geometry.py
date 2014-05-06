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

# Third party modules.
from PySide.QtGui import \
    (QLabel, QItemDelegate, QAction, QTableView, QToolBar, QComboBox,
     QHeaderView, QWidget, QSizePolicy, QVBoxLayout, QMessageBox, QValidator,
     QHBoxLayout, QStackedWidget)
from PySide.QtCore import Qt, QAbstractTableModel, QModelIndex

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    (_ParameterizedClassWidget, _ParameterWidget, UnitParameterWidget,
     AngleParameterWidget)
from pymontecarlo.ui.gui.util.widget import \
    MultiNumericalLineEdit, NumericalValidator, UnitComboBox
from pymontecarlo.ui.gui.util.tango import getIcon, color as c
from pymontecarlo.ui.gui.options.wizard.material import \
    MaterialListWidget, MaterialListDialog, MaterialDialog
from pymontecarlo.ui.gui.options.wizard.options import \
    _ExpandableOptionsWizardPage

from pymontecarlo.options.geometry import \
    (_Geometry, Substrate, _SubstrateBody, Inclusion, _InclusionBody,
     Sphere, _SphereBody, HorizontalLayers, _HorizontalSubstrateBody,
     VerticalLayers, _VerticalLeftSubstrateBody, _VerticalRightSubstrateBody)

from pymontecarlo.util.parameter import expand

# Globals and constants variables.

#--- Parameter widgets

TiltWidget = AngleParameterWidget
RotationWidget = AngleParameterWidget
DiameterWidget = UnitParameterWidget

class LayerListWidget(_ParameterWidget):

    class _MockLayer(object):

        def __init__(self, material, thickness_m):
            self.material = material
            self.thickness_m = thickness_m

        def __repr__(self):
            return '<_MockLayer(material=%s, thickness=%s m)>' % \
                (self.material, self.thickness_m)

    class _ThicknessValidator(NumericalValidator):

        def validate(self, value):
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

        def createEditor(self, parent, option, index):
            column = index.column()
            if column == 1:
                editor = MultiNumericalLineEdit(parent)
                editor.setStyleSheet("background: none")
                editor.setValidator(LayerListWidget._ThicknessValidator())
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

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Variables
        model = self._LayerModel()

        # Actions
        act_add = QAction(getIcon("list-add"), "Add material", self)
        act_remove = QAction(getIcon("list-remove"), "Remove material", self)

        # Widgets
        self._cb_unit = UnitComboBox('m')
        self._cb_unit.setUnit('um')

        self._tbl_layers = QTableView()
        self._tbl_layers.setModel(model)
        self._tbl_layers.setItemDelegate(self._LayerDelegate())
        header = self._tbl_layers.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        header.setStyleSheet('color: blue')

        self._tlb_layers = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tlb_layers.addWidget(spacer)
        self._tlb_layers.addAction(act_add)
        self._tlb_layers.addAction(act_remove)

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
            dialog = MaterialDialog()
        elif len(materials) == 1:
            dialog = MaterialDialog()
            dialog.setValue(materials[0])
        else:
            dialog = MaterialListDialog()
            dialog.setValues(materials)

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

    def values(self):
        factor = self._cb_unit.factor()

        layers = []
        for material, thickness in self._tbl_layers.model().layers():
            if not material or not thickness:
                continue
            thickness_m = np.array(thickness, ndmin=1) * factor
            layers.append(self._MockLayer(material, thickness_m))

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
        return not self._tbl_layers.isEnabled() and \
                not self._tlb_layers.isEnabled()

    def setReadOnly(self, state):
        self._tbl_layers.setEnabled(not state)
        self._tlb_layers.setEnabled(not state)

#--- Geometry widgets

class _GeometryWidget(_ParameterizedClassWidget):

    def _initUI(self):
        # Widgets
        self._txt_tilt = TiltWidget(_Geometry.tilt_rad)
        self._txt_rotation = RotationWidget(_Geometry.rotation_rad)

        # Layouts
        layout = _ParameterizedClassWidget._initUI(self)
        layout.addRow(c('Tilt', 'blue'), self._txt_tilt)
        layout.addRow(c('Rotation', 'blue'), self._txt_rotation)

        return layout

    def setValue(self, geometry):
        self._txt_tilt.setValues(geometry.tilt_rad)
        self._txt_rotation.setValues(geometry.rotation_rad)

class SubstrateWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName('Substrate')

    def _initUI(self):
        # Widgets
        self._lst_material = MaterialListWidget(_SubstrateBody.material)

        # Layouts
        layout = _GeometryWidget._initUI(self)
        layout.insertRow(0, QLabel(c("Material", 'blue')))
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

class InclusionWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Inclusion")

    def _initUI(self):
        # Widgets
        self._lst_substrate = MaterialListWidget(_SubstrateBody.material)
        self._lst_inclusion = MaterialListWidget(_InclusionBody.material)
        self._txt_diameter = DiameterWidget(_InclusionBody.diameter_m)

        # Layouts
        layout = _GeometryWidget._initUI(self)
        layout.insertRow(0, QLabel(c("Substrate", 'blue')))
        layout.insertRow(1, self._lst_substrate)
        layout.insertRow(2, QLabel(c("Inclusion", 'blue')))
        layout.insertRow(3, self._lst_inclusion)
        layout.insertRow(4, c("Inclusion diameter", 'blue'), self._txt_diameter)

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

class HorizontalLayersWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Horizontal layers")

    def _initUI(self):
        # Widgets
        self._lst_layer = LayerListWidget(HorizontalLayers.layers)
        self._lst_substrate = MaterialListWidget(_HorizontalSubstrateBody.material)
        self._lst_substrate.setRequired(False)

        # Layouts
        layout = _GeometryWidget._initUI(self)
        layout.insertRow(0, QLabel(c("Layer", 'blue')))
        layout.insertRow(1, self._lst_layer)
        layout.insertRow(2, QLabel(c("Substrate (optional)", 'blue')))
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

class VerticalLayersWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Vertical layers")

    def _initUI(self):
        # Widgets
        self._lst_left = MaterialListWidget(_VerticalLeftSubstrateBody.material)

        self._lst_layer = LayerListWidget(VerticalLayers.layers)
        self._lst_layer.setRequired(False)

        self._lst_right = MaterialListWidget(_VerticalRightSubstrateBody.material)

        self._txt_depth = UnitParameterWidget(VerticalLayers.depth_m)

        # Layouts
        layout = _GeometryWidget._initUI(self)

        sublayout = QHBoxLayout()

        subsublayout = QVBoxLayout()
        subsublayout.addWidget(QLabel(c("Left substrate", 'blue')))
        subsublayout.addWidget(self._lst_left)
        sublayout.addLayout(subsublayout)

        subsublayout = QVBoxLayout()
        subsublayout.addWidget(QLabel(c("Layer", 'blue')))
        subsublayout.addWidget(self._lst_layer)
        sublayout.addLayout(subsublayout)

        subsublayout = QVBoxLayout()
        subsublayout.addWidget(QLabel(c("Right substrate", 'blue')))
        subsublayout.addWidget(self._lst_right)
        sublayout.addLayout(subsublayout)

        layout.insertRow(0, sublayout)
        layout.insertRow(1, c("Depth", 'blue'), self._txt_depth)

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

class SphereWidget(_GeometryWidget):

    def __init__(self, parent=None):
        _GeometryWidget.__init__(self, parent=parent)
        self.setAccessibleName("Sphere")

    def _initUI(self):
        # Widgets
        self._lst_material = MaterialListWidget(_SphereBody.material)
        self._txt_diameter = DiameterWidget(_SphereBody.diameter_m)

        # Layouts
        layout = _ParameterizedClassWidget._initUI(self)
        layout.insertRow(0, QLabel(c("Material", 'blue')))
        layout.insertRow(1, self._lst_material)
        layout.insertRow(2, c("Sphere diameter", 'blue'), self._txt_diameter)

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

#--- Wizard page

class GeometryWizardPage(_ExpandableOptionsWizardPage):

    def __init__(self, options, parent=None):
        _ExpandableOptionsWizardPage.__init__(self, options, parent)
        self.setTitle('Geometry')

    def _initUI(self):
        # Variables
        self._widgets = {}

        # Widgets
        self._cb_geometry = QComboBox()

        self._wdg_geometry = QStackedWidget()
        policy = self._wdg_geometry.sizePolicy()
        policy.setVerticalStretch(True)
        self._wdg_geometry.setSizePolicy(policy)

        # Layouts
        layout = _ExpandableOptionsWizardPage._initUI(self)
        layout.addRow("Type of geometry", self._cb_geometry)
        layout.addRow(self._wdg_geometry)

        # Signals
        self._cb_geometry.currentIndexChanged.connect(self._onGeometryChanged)
        self._cb_geometry.currentIndexChanged.connect(self.valueChanged)

        return layout

    def _onGeometryChanged(self):
        newindex = self._cb_geometry.currentIndex()
        oldwidget = self._wdg_geometry.currentWidget()
        newwidget = self._wdg_geometry.widget(newindex)
        if newwidget is None:
            return

        try:
            newwidget.setValue(oldwidget.value())
        except:
            pass

        self._wdg_geometry.setCurrentIndex(newindex)

        # See https://qt-project.org/faq/answer/how_can_i_get_a_qstackedwidget_to_automatically_switch_size_depending_on_th
        oldwidget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        newwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._wdg_geometry.adjustSize()

    def initializePage(self):
        # Clear
        self._widgets.clear()
        for i in reversed(range(self._cb_geometry.count())):
            self._cb_geometry.removeItem(i)
            self._wdg_geometry.removeWidget(self._wdg_geometry.widget(i))

        # Populate combo box
        it = self._iter_widgets('pymontecarlo.ui.gui.options.wizard.geometry',
                                'GEOMETRIES')
        for clasz, widget_class, programs in it:
            widget = widget_class()
            widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

            self._widgets[clasz] = widget

            program_text = ', '.join(map(attrgetter('name'), programs))
            text = '{0} ({1})'.format(widget.accessibleName(), program_text)
            self._cb_geometry.addItem(text)
            self._wdg_geometry.addWidget(widget)

            widget.valueChanged.connect(self.valueChanged)

        # Select geometry
        geometry = self.options().geometry

        widget = self._widgets.get(geometry.__class__)
        if widget is None:
            raise ValueError('No widget for geometry class: %s' % \
                            geometry.__class__.__name__)

        widget.setValue(geometry)
        self._wdg_geometry.setCurrentWidget(widget)
        self._cb_geometry.setCurrentIndex(self._wdg_geometry.currentIndex())

    def validatePage(self):
        if not self._wdg_geometry.currentWidget().hasAcceptableInput():
            return False

        self.options().geometry = self._wdg_geometry.currentWidget().value()

        return True

    def expandCount(self):
        try:
            return len(expand(self._wdg_geometry.currentWidget().value()))
        except:
            return 1

def __run():
    import sys
    from PySide.QtGui import QApplication, QMainWindow
    from pymontecarlo.options.material import Material

    app = QApplication(sys.argv)
    window = QMainWindow(None)
#    widget = EnergyWidget(PencilBeam.energy_eV)
#    widget = AngleParameterWidget(PencilBeam.aperture_rad)
#    widget = ParticleParameterWidget(PencilBeam.particle)
#    widget.setValues([ELECTRON])
#    widget = OriginWidget(PencilBeam.origin_m)
#    widget = DirectionWidget(PencilBeam.direction)
#    widget.valuesChanged.connect(lambda: print(widget.values(), widget.hasAcceptableInput()))

    widget = VerticalLayersWidget()
    geo = VerticalLayers(Material.pure(25), Material.pure(26))
    geo.add_layer(Material.pure(13), 0.5e-6)
    widget.setValue(geo)

    window.setCentralWidget(widget)
    window.show()

    app.exec_()

    print(widget.hasAcceptableInput())
    print(widget.value().depth_m)

if __name__ == '__main__':
    __run()


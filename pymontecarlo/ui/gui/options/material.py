#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- Material widgets
================================================================================

.. module:: material
   :synopsis: Material widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.options.material

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import methodcaller
from itertools import product

# Third party modules.
from PySide.QtGui import \
    (QDialog, QLineEdit, QCheckBox, QRegExpValidator,
     QVBoxLayout, QLabel, QDialogButtonBox, QTableView, QItemDelegate,
     QHeaderView, QGridLayout, QToolBar, QAction, QMessageBox, QValidator,
     QWidget, QSizePolicy, QListView, QGroupBox, QPushButton, QHBoxLayout)
from PySide.QtCore import Qt, QRegExp, QAbstractTableModel, QModelIndex

import pyxray.element_properties as ep

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.periodictable import PeriodicTableDialog
from pymontecarlo.ui.gui.util.widget import \
    (MultiNumericalLineEdit, NumericalLineEdit, NumericalValidator,
     UnitComboBox)
from pymontecarlo.ui.gui.util.parameter import _ParameterWidget
from pymontecarlo.ui.gui.util.tango import getIcon
from pymontecarlo.ui.gui.util.registry import get_widget_class as _get_widget_class

from pymontecarlo.options.material import Material, VACUUM
from pymontecarlo.options.geometry import _Body

from pymontecarlo.util.multipleloop import combine

# Globals and constants variables.
from pymontecarlo.options.particle import PARTICLES, ELECTRON, PHOTON, POSITRON

class _FractionValidator(NumericalValidator):

    def validate(self, values):
        for value in values:
            if value < 0.0 or value > 1.0:
                return QValidator.Intermediate
        return QValidator.Acceptable

class _DensityValidator(NumericalValidator):

    def validate(self, value):
        if value <= 0.0:
            return QValidator.Intermediate
        return QValidator.Acceptable

class _AbsorptionEnergyValidator(NumericalValidator):

    def validate(self, values):
        for value in values:
            if value < 0.0:
                return QValidator.Intermediate
        return QValidator.Acceptable

class _CompositionModel(QAbstractTableModel):

    def __init__(self):
        QAbstractTableModel.__init__(self)
        self._compositions = []

    def rowCount(self, *args, **kwargs):
        return len(self._compositions)

    def columnCount(self, *args, **kwargs):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._compositions)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        zs, fractions = self._compositions[index.row()]
        column = index.column()
        if column == 0:
            if not zs:
                return 'none'
            else:
                return ', '.join(map(ep.symbol, sorted(zs)))
        elif column == 1:
            if not fractions:
                return '?'
            else:
                return ', '.join(map(str, fractions))

    def headerData(self, section , orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'Element'
            elif section == 1:
                return 'Weight fraction'
        elif orientation == Qt.Vertical:
            return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                            Qt.ItemIsEditable)

    def setData(self, index, values, role=Qt.EditRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._compositions)):
            return False

        row = index.row()
        column = index.column()
        self._compositions[row][column].clear()
        self._compositions[row][column].extend(values)

        self.dataChanged.emit(index, index)
        return True

    def insertRows(self, row, count=1, parent=None):
        if parent is None:
            parent = QModelIndex()
        self.beginInsertRows(QModelIndex(), row, row + count - 1)

        for _ in range(count):
            self._compositions.insert(row, ([], []))

        self.endInsertRows()
        return True

    def removeRows(self, row, count=1, parent=None):
        if parent is None:
            parent = QModelIndex()
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)

        for index in reversed(range(row, row + count)):
            self._compositions.pop(index)

        self.endRemoveRows()
        return True

    def compositions(self):
        rows = []
        for zs, fractions in self._compositions:
            if not fractions:
                fractions = '?'
            rows.append(product(zs, fractions))

        return [dict(c) for c in product(*rows)]

class _CompositionDelegate(QItemDelegate):

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        column = index.column()
        if column == 0:
            return None
        elif column == 1:
            editor = MultiNumericalLineEdit(parent)
            editor.setValidator(_FractionValidator())
            return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)
        column = index.column()
        if column == 1:
            if text != '?':
                editor.setText(text)

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

class MaterialDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Material')

        # Variables
        self._is_vacuum = False

        # Widgets
        btnvacuum = QPushButton("Vacuum")
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layouts
        layout = QVBoxLayout()
        layout.addLayout(self._initUI())

        sublayout = QHBoxLayout()
        sublayout.addWidget(btnvacuum)
        sublayout.addStretch()
        sublayout.addWidget(buttons)
        layout.addLayout(sublayout)

        self.setLayout(layout)

        # Signals
        btnvacuum.released.connect(self._onVacuum)
        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self._onCancel)

    def _initUI(self):
        # Variables
        model = _CompositionModel()

        # Actions
        act_add_element = QAction(getIcon("list-add"), "Add element", self)
        act_remove_element = QAction(getIcon("list-remove"), "Remove element", self)
        act_clear_element = QAction(getIcon("edit-clear"), "Clear", self)

        # Widgets
        self._txt_name = QLineEdit()
        self._txt_name.setEnabled(False)
        self._txt_name.setValidator(QRegExpValidator(QRegExp(r"^(?!\s*$).+")))

        self._chk_name_auto = QCheckBox('auto')
        self._chk_name_auto.setChecked(True)

        self._txt_density = NumericalLineEdit()
        self._txt_density.setEnabled(False)
        self._txt_density.setValidator(_DensityValidator())

        self._chk_density_user = QCheckBox('user defined')
        self._chk_density_user.setChecked(False)

        self._tbl_composition = QTableView()
        self._tbl_composition.setModel(model)
        self._tbl_composition.setItemDelegate(_CompositionDelegate())
        header = self._tbl_composition.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        header.setStyleSheet('color: blue')

        self._tlb_composition = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tlb_composition.addWidget(spacer)
        self._tlb_composition.addAction(act_add_element)
        self._tlb_composition.addAction(act_remove_element)
        self._tlb_composition.addAction(act_clear_element)

        self._wdg_abs_energies = {}
        for particle in PARTICLES:
            label = QLabel(str(particle))
            label.setStyleSheet("color: blue")
            txt_energy = MultiNumericalLineEdit()
            txt_energy.setAccessibleName(str(particle))
            txt_energy.setValidator(_AbsorptionEnergyValidator())
            cb_unit = UnitComboBox('eV')
            self._wdg_abs_energies[particle] = (label, txt_energy, cb_unit)

        # Layouts
        layout = QVBoxLayout()

        sublayout = QGridLayout()
        sublayout.addWidget(QLabel("Name"), 0, 0)
        sublayout.addWidget(self._txt_name, 0, 1)
        sublayout.addWidget(self._chk_name_auto, 0, 2)
        sublayout.addWidget(QLabel("Density (kg/m3)"), 1, 0)
        sublayout.addWidget(self._txt_density, 1, 1)
        sublayout.addWidget(self._chk_density_user, 1, 2)
        layout.addLayout(sublayout)

        box_composition = QGroupBox('Composition')
        boxlayout = QVBoxLayout()
        boxlayout.addWidget(self._tbl_composition)
        boxlayout.addWidget(self._tlb_composition)
        box_composition.setLayout(boxlayout)
        layout.addWidget(box_composition)

        box_absorption_energy = QGroupBox('Absorption energy')
        boxlayout = QGridLayout()
        for row, particle in enumerate(sorted(self._wdg_abs_energies.keys())):
            label, txt_energy, cb_unit = self._wdg_abs_energies[particle]
            boxlayout.addWidget(label, row, 0)
            boxlayout.addWidget(txt_energy, row, 1)
            boxlayout.addWidget(cb_unit, row, 2)
        box_absorption_energy.setLayout(boxlayout)
        layout.addWidget(box_absorption_energy)

        # Signals
        self._txt_name.textChanged.connect(self._onNameChanged)
        self._chk_name_auto.stateChanged.connect(self._onNameAutoChanged)

        self._txt_density.textChanged.connect(self._onDensityChanged)
        self._chk_density_user.stateChanged.connect(self._onDensityUserChanged)

        self._tbl_composition.doubleClicked.connect(self._onCompositionDoubleClicked)

        model.dataChanged.connect(self._onCompositionChanged)
        model.rowsInserted.connect(self._onCompositionChanged)
        model.rowsRemoved.connect(self._onCompositionChanged)

        act_add_element.triggered.connect(self._onCompositionAdd)
        act_remove_element.triggered.connect(self._onCompositionRemove)
        act_clear_element.triggered.connect(self._onCompositionClear)

        for _, txt_energy, _ in self._wdg_abs_energies.values():
            txt_energy.textChanged.connect(self._onAbsEnergyChanged)

        return layout

    def _onNameChanged(self):
        if self._txt_name.hasAcceptableInput() or \
                not self._txt_name.isEnabled():
            self._txt_name.setStyleSheet("background: none")
        else:
            self._txt_name.setStyleSheet("background: pink")

    def _onNameAutoChanged(self):
        self._txt_name.setEnabled(not self._chk_name_auto.isChecked())
        self._txt_name.textChanged.emit(self._txt_name.text())

    def _onDensityChanged(self):
        if self._txt_density.hasAcceptableInput() or \
                not self._txt_density.isEnabled():
            self._txt_density.setStyleSheet("background: none")
        else:
            self._txt_density.setStyleSheet("background: pink")

    def _onDensityUserChanged(self):
        self._txt_density.setEnabled(self._chk_density_user.isChecked())
        self._txt_density.textChanged.emit(self._txt_density.text())

    def _onCompositionChanged(self):
        compositions = self._tbl_composition.model().compositions()

        if len(compositions) > 1:
            self._chk_name_auto.setChecked(True)
            self._chk_name_auto.setEnabled(False)
            self._chk_density_user.setChecked(False)
            self._chk_density_user.setEnabled(False)
        else:
            self._chk_name_auto.setEnabled(True)
            self._chk_density_user.setEnabled(True)

        try:
            for composition in compositions:
                Material.calculate_composition(composition)
        except:
            self._tbl_composition.setStyleSheet("background: pink")
        else:
            self._tbl_composition.setStyleSheet("background: none")

    def _onCompositionDoubleClicked(self, index):
        if index.column() != 0:
            return

        model = self._tbl_composition.model()

        dialog = PeriodicTableDialog()
        dialog.setMultipleSelection(True)
        dialog.setRequiresSelection(True)

        text = model.data(index)
        if text != 'none':
            dialog.setSelection(text.split(','))

        if not dialog.exec_():
            return

        model.setData(index, dialog.selection())

    def _onCompositionAdd(self):
        index = self._tbl_composition.selectionModel().currentIndex()
        model = self._tbl_composition.model()
        model.insertRows(index.row() + 1)

        # Show periodic table right away
        index = model.createIndex(index.row() + 1, 0)
        self._onCompositionDoubleClicked(index)

    def _onCompositionRemove(self):
        selection = self._tbl_composition.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Composition", "Select a row")
            return

        model = self._tbl_composition.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            model.removeRow(row)

    def _onCompositionClear(self):
        model = self._tbl_composition.model()
        for row in reversed(range(model.rowCount())):
            model.removeRow(row)

    def _onAbsEnergyChanged(self):
        txt_energy = self.sender()
        if txt_energy.hasAcceptableInput():
            txt_energy.setStyleSheet("background: none")
        else:
            txt_energy.setStyleSheet("background: pink")

    def _onOk(self):
        if self.isReadOnly():
            self.reject()
            return

        errors = []

        if not self._chk_name_auto.isChecked() and \
                not self._txt_name.hasAcceptableInput():
            errors.append("Invalid name")

        if self._chk_density_user.isChecked() and \
                not self._txt_density.hasAcceptableInput():
            errors.append("Invalid density")

        compositions = self._tbl_composition.model().compositions()
        if not compositions:
            errors.append("No composition")
        for composition in compositions:
            try:
                Material.calculate_composition(composition)
            except Exception as ex:
                errors.append(str(ex))

        for _, txt_energy, _ in self._wdg_abs_energies.values():
            if not txt_energy.hasAcceptableInput():
                name = txt_energy.accessibleName()
                errors.append('Invalid absorption energy for %s' % name)

        if errors:
            message = 'The following error(s) occur(s):\n- ' + '\n- '.join(errors)
            QMessageBox.critical(self, 'Material', message)
            return

        self._is_vacuum = False

        self.accept()

    def _onCancel(self):
        self.reject()

    def _onVacuum(self):
        self._is_vacuum = True
        self.accept()

    def _getParametersDict(self):
        params = {}

        if self._chk_name_auto.isChecked():
            name = None
        else:
            name = self._txt_name.text()
        params['name'] = [name]

        if self._chk_density_user.isChecked():
            density = self._txt_density.value()
        else:
            density = None
        params['density_kg_m3'] = [density]

        params['composition'] = self._tbl_composition.model().compositions()

        for particle in self._wdg_abs_energies.keys():
            _, txt_energy, cb_unit = self._wdg_abs_energies[particle]
            values = txt_energy.values() * cb_unit.factor()
            values = values.tolist()
            if len(values) == 0:
                values = [Material.DEFAULT_ABSORPTION_ENERGY_eV]
            params[str(particle)] = values

        return params

    def _generateName(self, parameters, varied):
        name = parameters.pop('name')
        if name is None:
            name = Material.generate_name(parameters['composition'])

        parts = [name]
        for key in varied:
            if key == 'composition': continue
            parts.append('{0:s}={1:n}'.format(key, parameters[key]))
        return '+'.join(parts)

    def _createMaterial(self, parameters, varied):
        # Name
        name = self._generateName(parameters, varied)

        # Absorption energy
        absorption_energy = {ELECTRON: parameters.pop(str(ELECTRON)),
                             PHOTON: parameters.pop(str(PHOTON)),
                             POSITRON: parameters.pop(str(POSITRON))}

        return Material(name=name, absorption_energy_eV=absorption_energy,
                        **parameters)

    def values(self):
        if self._is_vacuum:
            return [VACUUM]

        prm_values = [(key, value) for key, value in self._getParametersDict().items()]
        combinations, names, varied = combine(prm_values)

        materials = []
        for combination in combinations:
            parameters = dict(zip(names, combination))
            materials.append(self._createMaterial(parameters, varied))

        return materials

    def setValue(self, material):
        # Name
        self._txt_name.setText(material.name)
        self._chk_name_auto.setChecked(False)

        # Density
        self._txt_density.setText(str(material.density_kg_m3))
        self._chk_density_user.setChecked(True)

        # Composition
        composition = material.composition

        model = self._tbl_composition.model()
        model.removeRows(0, model.rowCount())
        model.insertRows(1, len(composition))

        for row, z in enumerate(sorted(composition.keys())):
            model.setData(model.index(row, 0), [z])
            model.setData(model.index(row, 1), [composition[z]])

        # Absorption energy
        for _, txt_energy, cb_unit in self._wdg_abs_energies.values():
            txt_energy.setText('')
            cb_unit.setUnit('eV')

        for particle, energy in material.absorption_energy_eV.items():
            self._wdg_abs_energies[particle][1].setValues(energy)

    def setReadOnly(self, state):
        style = 'color: none' if state else 'color: blue'

        self._txt_name.setReadOnly(state)
        self._chk_name_auto.setEnabled(not state)
        self._txt_density.setReadOnly(state)
        self._chk_density_user.setEnabled(not state)
        self._tbl_composition.setEnabled(not state)
        self._tbl_composition.horizontalHeader().setStyleSheet(style)
        self._tlb_composition.setVisible(not state)
        for label, txt_energy, cb_unit in self._wdg_abs_energies.values():
            label.setStyleSheet(style)
            txt_energy.setReadOnly(state)
            cb_unit.setEnabled(not state)

    def isReadOnly(self):
        return self._txt_name.isReadOnly() and \
            not self._chk_name_auto.isEnabled() and \
            self._txt_density.isReadOnly() and \
            not self._chk_density_user.isEnabled() and \
            not self._tbl_composition.isEnabled() and \
            not self._tlb_composition.isVisible() and \
            all(map(lambda w: w[1].isReadOnly() and not w[2].isEnabled(),
                    self._wdg_abs_energies.values()))

class _MaterialModel(QAbstractTableModel):

    def __init__(self):
        QAbstractTableModel.__init__(self)
        self._materials = []

    def rowCount(self, *args, **kwargs):
        return len(self._materials)

    def columnCount(self, *args, **kwargs):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._materials)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        material = self._materials[index.row()]
        if material is None:
            return ''
        return material.name

    def headerData(self, section , orientation, role):
        if role != Qt.DisplayRole:
            return None
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._materials)):
            return False

        row = index.row()
        self._materials[row] = value

        self.dataChanged.emit(index, index)
        return True

    def insertRows(self, row, count=1, parent=None):
        if parent is None:
            parent = QModelIndex()
        self.beginInsertRows(QModelIndex(), row, row + count - 1)

        for _ in range(count):
            self._materials.insert(row, None)

        self.endInsertRows()
        return True

    def removeRows(self, row, count=1, parent=None):
        if parent is None:
            parent = QModelIndex()
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)

        for index in reversed(range(row, row + count)):
            self._materials.pop(index)

        self.endRemoveRows()
        return True

    def material(self, index):
        return self._materials[index.row()]

    def materials(self):
        return list(self._materials)

class MaterialListWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Variables
        model = _MaterialModel()
        self._material_class = Material

        # Actions
        act_add = QAction(getIcon("list-add"), "Add material", self)
        act_remove = QAction(getIcon("list-remove"), "Remove material", self)
        act_clear = QAction(getIcon("edit-clear"), "Clear", self)

        # Widgets
        self._lst_materials = QListView()
        self._lst_materials.setModel(model)
        self._lst_materials.setSelectionMode(QListView.SelectionMode.MultiSelection)

        self._tlb_materials = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tlb_materials.addWidget(spacer)
        self._tlb_materials.addAction(act_add)
        self._tlb_materials.addAction(act_remove)
        self._tlb_materials.addAction(act_clear)

        # Layouts
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._lst_materials, 1)
        layout.addWidget(self._tlb_materials)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._lst_materials.doubleClicked.connect(self._onDoubleClicked)

        model.dataChanged.connect(self.valuesChanged)
        model.rowsInserted.connect(self.valuesChanged)
        model.rowsRemoved.connect(self.valuesChanged)

        act_add.triggered.connect(self._onAdd)
        act_remove.triggered.connect(self._onRemove)
        act_clear.triggered.connect(self._onClear)

        self.validationRequested.emit()

    def _insertMaterials(self, row, materials):
        model = self._lst_materials.model()
        model.insertRows(row, len(materials))

        for i, material in enumerate(materials):
            model.setData(model.index(row + i, 0), material)

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._lst_materials.setStyleSheet("background: none")
        else:
            self._lst_materials.setStyleSheet("background: pink")

    def _onDoubleClicked(self, index):
        model = self._lst_materials.model()
        material = model.material(index)

        if material is VACUUM:
            return

        dialog = get_dialog_class(material.__class__)()
        dialog.setValue(material)
        dialog.setReadOnly(self.isReadOnly())
        if not dialog.exec_():
            return

        row = index.row()
        materials = dialog.values()
        model.removeRow(row)
        self._insertMaterials(row, materials)

    def _onAdd(self):
        row = self._lst_materials.selectionModel().currentIndex().row() + 1

        dialog = get_dialog_class(self._material_class)()
        if not dialog.exec_():
            return

        materials = dialog.values()
        self._insertMaterials(row, materials)

    def _onRemove(self):
        selection = self._lst_materials.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Materials", "Select a material")
            return

        model = self._lst_materials.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            model.removeRow(row)

    def _onClear(self):
        model = self._lst_materials.model()
        for row in reversed(range(model.rowCount())):
            model.removeRow(row)

    def setValues(self, materials):
        materials = np.array(materials, ndmin=1)
        model = self._lst_materials.model()
        model.removeRows(0, model.rowCount())
        self._insertMaterials(0, materials)

    def values(self):
        return self._lst_materials.model().materials()

    def isReadOnly(self):
        return not self._tlb_materials.isVisible()

    def setReadOnly(self, state):
        self._tlb_materials.setVisible(not state)

    def materialClass(self):
        return self._material_class

    def setMaterialClass(self, clasz):
        self._material_class = clasz

class MaterialListDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Materials")

        # Widgets
        self._lst_materials = MaterialListWidget(_Body.material)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self._lst_materials)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # Signals
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def values(self):
        return self._lst_materials.values()

    def setValues(self, materials):
        self._lst_materials.setValues(materials)

    def isReadOnly(self):
        return self._lst_materials.isReadOnly()

    def setReadOnly(self, state):
        self._lst_materials.setReadOnly(state)

    def materialClass(self):
        return self._lst_materials.materialClass()

    def setMaterialClass(self, clasz):
        self._lst_materials.setMaterialClass(clasz)

def get_dialog_class(clasz):
    return _get_widget_class('pymontecarlo.ui.gui.options.material', clasz)

def __run():
    import sys
    from PySide.QtGui import QApplication

    material = Material({5: 0.5, 6: 0.5}, absorption_energy_eV={ELECTRON: 60.0})

    app = QApplication(sys.argv)

    dialog = MaterialDialog(None)
    dialog.setValue(material)
    if dialog.exec_():
        for material in dialog.values():
            print(repr(material))

#    dialog = MaterialListDialog()
#    dialog.setValues([material])
#    dialog.show()

#    window = QMainWindow()
#    window.setCentralWidget(widget)
#    window.show()

    app.exec_()

#    print(widget.values())

if __name__ == '__main__':
    __run()

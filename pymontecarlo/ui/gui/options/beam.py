#!/usr/bin/env python
"""
================================================================================
:mod:`beam` -- Beam widgets
================================================================================

.. module:: beam
   :synopsis: Beam widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.options.beam

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
from itertools import product
from operator import itemgetter, methodcaller

# Third party modules.
from PySide.QtGui import QCheckBox, QHBoxLayout, QFormLayout, QLabel

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    (_ParameterizedClassWidget, _ParameterWidget, UnitParameterWidget,
     AngleParameterWidget)
from pymontecarlo.ui.gui.util.widget import UnitComboBox, MultiNumericalLineEdit
from pymontecarlo.ui.gui.util.registry import get_widget_class as _get_widget_class

from pymontecarlo.options.beam import PencilBeam, GaussianBeam
from pymontecarlo.options.particle import PARTICLES

# Globals and constants variables.

#--- Parameter widgets

EnergyWidget = UnitParameterWidget

class ParticleWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._widgets = {}
        for particle in sorted(PARTICLES):
            self._widgets[particle] = QCheckBox(str(particle))

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for particle in sorted(self._widgets.keys()):
            layout.addWidget(self._widgets[particle])
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        for widget in self._widgets.values():
            widget.stateChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            for widget in self._widgets.values():
                widget.setStyleSheet("background: none")
        else:
            for widget in self._widgets.values():
                widget.setStyleSheet("background: pink")

    def values(self):
        values = []
        for particle, widget in self._widgets.items():
            if widget.isChecked():
                values.append(particle)
        return values

    def setValues(self, values):
        values = np.array(values, ndmin=1)
        for particle, widget in self._widgets.items():
            widget.setChecked(particle in values)

    def isReadOnly(self):
        return all(map(lambda w: not w.isEnabled(), self._widgets.values()))

    def setReadOnly(self, state):
        for widget in self._widgets.values():
            widget.setEnabled(not state)

    def setParticleEnabled(self, particle, state):
        self._widgets[particle].setEnabled(state)

    def isParticleEnabled(self, particle):
        return self._widgets[particle].isEnabled()

    def setParticlesEnabled(self, state):
        for widget in self._widgets.values():
            widget.setEnabled(state)

    def areParticlesEnabled(self):
        return all(map(methodcaller('isEnabled'), self._widgets.values()))

class OriginWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._lbl_x = QLabel('x')
        self._lbl_x.setStyleSheet("color: blue")
        self._txt_x = MultiNumericalLineEdit()

        self._lbl_y = QLabel('y')
        self._lbl_y.setStyleSheet("color: blue")
        self._txt_y = MultiNumericalLineEdit()

        self._lbl_z = QLabel('z')
        self._lbl_z.setStyleSheet("color: blue")
        self._txt_z = MultiNumericalLineEdit()

        self._cb_unit = UnitComboBox(parameter.unit)

        # Layouts
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layout.addRow(self._lbl_x, self._txt_x)
        layout.addRow(self._lbl_y, self._txt_y)
        layout.addRow(self._lbl_z, self._txt_z)
        layout.addRow('Unit', self._cb_unit)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_x.textChanged.connect(self.valuesChanged)
        self._txt_y.textChanged.connect(self.valuesChanged)
        self._txt_z.textChanged.connect(self.valuesChanged)
        self._cb_unit.currentIndexChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_x.setStyleSheet("background: none")
            self._txt_y.setStyleSheet("background: none")
            self._txt_z.setStyleSheet("background: none")
        else:
            self._txt_x.setStyleSheet("background: pink")
            self._txt_y.setStyleSheet("background: pink")
            self._txt_z.setStyleSheet("background: pink")

    def values(self):
        xs = self._txt_x.values() * self._cb_unit.factor()
        ys = self._txt_y.values() * self._cb_unit.factor()
        zs = self._txt_z.values() * self._cb_unit.factor()
        return list(product(xs, ys, zs))

    def setValues(self, values):
        values = np.array(values, ndmin=1)
        self._txt_x.setValues(list(map(itemgetter(0), values)))
        self._txt_y.setValues(list(map(itemgetter(1), values)))
        self._txt_z.setValues(list(map(itemgetter(2), values)))
        self._cb_unit.setUnit('m')

    def isReadOnly(self):
        return self._txt_x.isReadOnly() and \
                self._txt_y.isReadOnly() and \
                self._txt_z.isReadOnly() and \
                not self._cb_unit.isEnabled()

    def setReadOnly(self, state):
        style = 'color: none' if state else 'color: blue'
        self._lbl_x.setStyleSheet(style)
        self._txt_x.setReadOnly(state)
        self._lbl_y.setStyleSheet(style)
        self._txt_y.setReadOnly(state)
        self._lbl_z.setStyleSheet(style)
        self._txt_z.setReadOnly(state)
        self._cb_unit.setEnabled(not state)

    def hasAcceptableInput(self):
        if not _ParameterWidget.hasAcceptableInput(self):
            return False

        if not self._txt_x.hasAcceptableInput():
            return False
        if not self._txt_y.hasAcceptableInput():
            return False
        if not self._txt_z.hasAcceptableInput():
            return False

        return True

class DirectionWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._lbl_u = QLabel('u')
        self._lbl_u.setStyleSheet("color: blue")
        self._txt_u = MultiNumericalLineEdit()

        self._lbl_v = QLabel('v')
        self._lbl_v.setStyleSheet("color: blue")
        self._txt_v = MultiNumericalLineEdit()

        self._lbl_w = QLabel('w')
        self._lbl_w.setStyleSheet("color: blue")
        self._txt_w = MultiNumericalLineEdit()

        # Layouts
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layout.addRow(self._lbl_u, self._txt_u)
        layout.addRow(self._lbl_v, self._txt_v)
        layout.addRow(self._lbl_w, self._txt_w)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_u.textChanged.connect(self.valuesChanged)
        self._txt_v.textChanged.connect(self.valuesChanged)
        self._txt_w.textChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_u.setStyleSheet("background: none")
            self._txt_v.setStyleSheet("background: none")
            self._txt_w.setStyleSheet("background: none")
        else:
            self._txt_u.setStyleSheet("background: pink")
            self._txt_v.setStyleSheet("background: pink")
            self._txt_w.setStyleSheet("background: pink")

    def values(self):
        us = self._txt_u.values()
        vs = self._txt_v.values()
        ws = self._txt_w.values()
        return list(product(us, vs, ws))

    def setValues(self, values):
        values = np.array(values, ndmin=1)
        self._txt_u.setValues(list(map(itemgetter(0), values)))
        self._txt_v.setValues(list(map(itemgetter(1), values)))
        self._txt_w.setValues(list(map(itemgetter(2), values)))

    def isReadOnly(self):
        return self._txt_u.isReadOnly() and \
                self._txt_v.isReadOnly() and \
                self._txt_w.isReadOnly()

    def setReadOnly(self, state):
        style = 'color: none' if state else 'color: blue'
        self._lbl_u.setStyleSheet(style)
        self._txt_u.setReadOnly(state)
        self._lbl_v.setStyleSheet(style)
        self._txt_v.setReadOnly(state)
        self._lbl_w.setStyleSheet(style)
        self._txt_w.setReadOnly(state)

    def hasAcceptableInput(self):
        if not _ParameterWidget.hasAcceptableInput(self):
            return False

        if not self._txt_u.hasAcceptableInput():
            return False
        if not self._txt_v.hasAcceptableInput():
            return False
        if not self._txt_w.hasAcceptableInput():
            return False

        return True

ApertureWidget = AngleParameterWidget

DiameterWidget = UnitParameterWidget

#--- Beam widgets

class _BeamWidget(_ParameterizedClassWidget):
    pass

class PencilBeamWidget(_BeamWidget):

    def __init__(self, parent=None):
        _BeamWidget.__init__(self, parent)
        self.setAccessibleName("Pencil beam")

    def _initUI(self):
        # Widgets
        self._lbl_energy = QLabel('Initial energy')
        self._lbl_energy.setStyleSheet("color: blue")
        self._wdg_energy = EnergyWidget(PencilBeam.energy_eV)

        self._lbl_particle = QLabel('Type of particle')
        self._lbl_particle.setStyleSheet("color: blue")
        self._wdg_particle = ParticleWidget(PencilBeam.particle)

        self._lbl_origin = QLabel('Origin')
        self._lbl_origin.setStyleSheet("color: blue")
        self._wdg_origin = OriginWidget(PencilBeam.origin_m)

        self._lbl_direction = QLabel('Direction')
        self._lbl_direction.setStyleSheet("color: blue")
        self._wdg_direction = DirectionWidget(PencilBeam.direction)

        self._lbl_aperture = QLabel('Aperture')
        self._lbl_aperture.setStyleSheet("color: blue")
        self._wdg_aperture = ApertureWidget(PencilBeam.aperture_rad)

        # Layouts
        layout = _BeamWidget._initUI(self)
        layout.addRow(self._lbl_energy, self._wdg_energy)
        layout.addRow(self._lbl_particle, self._wdg_particle)
        layout.addRow(self._lbl_origin, self._wdg_origin)
        layout.addRow(self._lbl_direction, self._wdg_direction)
        layout.addRow(self._lbl_aperture, self._wdg_aperture)

        return layout

    def value(self):
        return PencilBeam(energy_eV=self._wdg_energy.values(),
                          particle=self._wdg_particle.values(),
                          origin_m=self._wdg_origin.values(),
                          direction=self._wdg_direction.values(),
                          aperture_rad=self._wdg_aperture.values())

    def setValue(self, beam):
        if hasattr(beam, 'energy_eV'):
            self._wdg_energy.setValues(beam.energy_eV)
        if hasattr(beam, 'particle'):
            self._wdg_particle.setValues(beam.particle)
        if hasattr(beam, 'origin_m'):
            self._wdg_origin.setValues(beam.origin_m)
        if hasattr(beam, 'direction'):
            self._wdg_direction.setValues(beam.direction)
        if hasattr(beam, 'aperture_rad'):
            self._wdg_aperture.setValues(beam.aperture_rad)

    def setReadOnly(self, state):
        _BeamWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_energy.setStyleSheet(style)
        self._lbl_particle.setStyleSheet(style)
        self._lbl_origin.setStyleSheet(style)
        self._lbl_direction.setStyleSheet(style)
        self._lbl_aperture.setStyleSheet(style)

    def setParticleEnabled(self, particle, state):
        self._wdg_particle.setParticleEnabled(particle, state)

    def isParticleEnabled(self, particle):
        return self._wdg_particle.isParticleEnabled(particle)

    def setParticlesEnabled(self, state):
        self._wdg_particle.setParticlesEnabled(state)

    def areParticlesEnabled(self):
        return self._wdg_particle.areParticlesEnabled()

class GaussianBeamWidget(PencilBeamWidget):

    def __init__(self, parent=None):
        PencilBeamWidget.__init__(self, parent)
        self.setAccessibleName("Gaussian beam")

    def _initUI(self):
        # Widgets
        self._lbl_diameter = QLabel('Diameter')
        self._lbl_diameter.setStyleSheet('color: blue')
        self._wdg_diameter = DiameterWidget(GaussianBeam.diameter_m)

        # Layouts
        layout = PencilBeamWidget._initUI(self)
        layout.addRow(self._lbl_diameter, self._wdg_diameter)

        return layout

    def value(self):
        return GaussianBeam(energy_eV=self._wdg_energy.values(),
                            diameter_m=self._wdg_diameter.values(),
                            particle=self._wdg_particle.values(),
                            origin_m=self._wdg_origin.values(),
                            direction=self._wdg_direction.values(),
                            aperture_rad=self._wdg_aperture.values())

    def setValue(self, beam):
        PencilBeamWidget.setValue(self, beam)
        if hasattr(beam, 'diameter_m'):
            self._wdg_diameter.setValues(beam.diameter_m)

    def setReadOnly(self, state):
        PencilBeamWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_diameter.setStyleSheet(style)

#--- Functions

def get_widget_class(clasz):
    return _get_widget_class('pymontecarlo.ui.gui.options.beam', clasz)

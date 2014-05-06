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
from itertools import product
from operator import itemgetter, attrgetter

# Third party modules.
from PySide.QtGui import \
    QCheckBox, QHBoxLayout, QFormLayout, QComboBox, QStackedWidget

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    (_ParameterizedClassWidget, _ParameterWidget, UnitParameterWidget,
     AngleParameterWidget)
from pymontecarlo.ui.gui.util.widget import UnitComboBox, MultiNumericalLineEdit
from pymontecarlo.ui.gui.util.tango import color as c
from pymontecarlo.ui.gui.options.options import _ExpandableOptionsWizardPage

from pymontecarlo.options.beam import PencilBeam, GaussianBeam
from pymontecarlo.options.particle import PARTICLES

from pymontecarlo.util.parameter import expand

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

class OriginWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._txt_x = MultiNumericalLineEdit()
        self._txt_y = MultiNumericalLineEdit()
        self._txt_z = MultiNumericalLineEdit()
        self._cb_unit = UnitComboBox(parameter.unit)

        # Layouts
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addRow(c('x', 'blue'), self._txt_x)
        layout.addRow(c('y', 'blue'), self._txt_y)
        layout.addRow(c('z', 'blue'), self._txt_z)
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
                self._txt_z.isReadOnly()

    def setReadOnly(self, state):
        self._txt_x.setReadOnly(state)
        self._txt_y.setReadOnly(state)
        self._txt_z.setReadOnly(state)

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
        self._txt_u = MultiNumericalLineEdit()
        self._txt_v = MultiNumericalLineEdit()
        self._txt_w = MultiNumericalLineEdit()

        # Layouts
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addRow(c('u', 'blue'), self._txt_u)
        layout.addRow(c('v', 'blue'), self._txt_v)
        layout.addRow(c('w', 'blue'), self._txt_w)
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
        self._txt_u.setReadOnly(state)
        self._txt_v.setReadOnly(state)
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
        self._wdg_energy = EnergyWidget(PencilBeam.energy_eV)
        self._wdg_particle = ParticleWidget(PencilBeam.particle)
        self._wdg_origin = OriginWidget(PencilBeam.origin_m)
        self._wdg_direction = DirectionWidget(PencilBeam.direction)
        self._wdg_aperture = ApertureWidget(PencilBeam.aperture_rad)

        # Layouts
        layout = _BeamWidget._initUI(self)
        layout.addRow(c('Initial energy', 'blue'), self._wdg_energy)
        layout.addRow(c('Type of particle', 'blue'), self._wdg_particle)
        layout.addRow(c('Origin', 'blue'), self._wdg_origin)
        layout.addRow(c('Direction', 'blue'), self._wdg_direction)
        layout.addRow(c('Aperture', 'blue'), self._wdg_aperture)

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

class GaussianBeamWidget(PencilBeamWidget):

    def __init__(self, parent=None):
        PencilBeamWidget.__init__(self, parent)
        self.setAccessibleName("Gaussian beam")

    def _initUI(self):
        # Widgets
        self._wdg_diameter = DiameterWidget(GaussianBeam.diameter_m)

        # Layouts
        layout = PencilBeamWidget._initUI(self)
        layout.addRow(c('Diameter', 'blue'), self._wdg_diameter)

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

#--- Wizard page

class BeamWizardPage(_ExpandableOptionsWizardPage):

    def __init__(self, options, parent=None):
        _ExpandableOptionsWizardPage.__init__(self, options, parent)
        self.setTitle('Beam')

    def _initUI(self):
        # Variables
        self._widgets = {}

        # Widgets
        self._cb_beam = QComboBox()
        self._wdg_beam = QStackedWidget()

        # Layouts
        layout = _ExpandableOptionsWizardPage._initUI(self)
        layout.addRow("Type of beam", self._cb_beam)
        layout.addRow(self._wdg_beam)

        # Signals
        self._cb_beam.currentIndexChanged.connect(self._onBeamChanged)
        self._cb_beam.currentIndexChanged.connect(self.valueChanged)

        return layout

    def _onBeamChanged(self):
        newindex = self._cb_beam.currentIndex()
        oldwidget = self._wdg_beam.currentWidget()
        newwidget = self._wdg_beam.widget(newindex)

        try:
            newwidget.setValue(oldwidget.value())
        except:
            pass

        self._wdg_beam.setCurrentIndex(newindex)

    def initializePage(self):
        # Clear
        self._widgets.clear()
        for i in reversed(range(self._cb_beam.count())):
            self._cb_beam.removeItem(i)
            self._wdg_beam.removeWidget(self._wdg_beam.widget(i))

        # Populate combo box
        it = self._iter_widgets('pymontecarlo.ui.gui.options.beam', 'BEAMS')
        for clasz, widget_class, programs in it:
            widget = widget_class()
            self._widgets[clasz] = widget

            program_text = ', '.join(map(attrgetter('name'), programs))
            text = '{0} ({1})'.format(widget.accessibleName(), program_text)
            self._cb_beam.addItem(text)
            self._wdg_beam.addWidget(widget)

            widget.valueChanged.connect(self.valueChanged)

        # Select beam
        beam = self.options().beam

        widget = self._widgets.get(beam.__class__)
        if widget is None:
            raise ValueError('No widget for beam class: %s' % beam.__class__.__name__)

        widget.setValue(beam)
        self._wdg_beam.setCurrentWidget(widget)
        self._cb_beam.setCurrentIndex(self._wdg_beam.currentIndex())

    def validatePage(self):
        if not self._wdg_beam.currentWidget().hasAcceptableInput():
            return False

        self.options().beam = self._wdg_beam.currentWidget().value()

        return True

    def expandCount(self):
        try:
            return len(expand(self._wdg_beam.currentWidget().value()))
        except:
            return 1

def __run():
    import sys
    from PySide.QtGui import QApplication, QMainWindow

    app = QApplication(sys.argv)
    window = QMainWindow(None)
#    widget = EnergyWidget(PencilBeam.energy_eV)
#    widget = AngleParameterWidget(PencilBeam.aperture_rad)
#    widget = ParticleParameterWidget(PencilBeam.particle)
#    widget.setValues([ELECTRON])
#    widget = OriginWidget(PencilBeam.origin_m)
#    widget = DirectionWidget(PencilBeam.direction)
#    widget.valuesChanged.connect(lambda: print(widget.values(), widget.hasAcceptableInput()))

    widget = GaussianBeamWidget()
    widget.setValue(GaussianBeam([5000.0, 6000.0], 10.0))

    window.setCentralWidget(widget)
    window.show()
    app.exec_()

    print(widget.hasAcceptableInput(), widget.value())

if __name__ == '__main__':
    __run()


#!/usr/bin/env python
"""
================================================================================
:mod:`beam` -- Beam wizard page
================================================================================

.. module:: beam
   :synopsis: Beam wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.beam

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter

# Third party modules.
from PySide.QtGui import QComboBox, QStackedWidget


# Local modules.
from pymontecarlo.ui.gui.options.wizard.options import \
    _ExpandableOptionsWizardPage

from pymontecarlo.util.parameter import expand

# Globals and constants variables.

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
        if newwidget is None:
            return

        try:
            newwidget.setValue(oldwidget.value())
        except:
            newwidget.setValue(self.options().beam)

        self._wdg_beam.setCurrentIndex(newindex)

    def initializePage(self):
        _ExpandableOptionsWizardPage.initializePage(self)

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

            widget.setParticlesEnabled(False)
            for program in programs:
                converter = program.converter_class
                for particle in converter.PARTICLES:
                    widget.setParticleEnabled(particle, True)

            widget.valueChanged.connect(self.valueChanged)

        # Select beam
        beam = self.options().beam

        widget = self._widgets.get(beam.__class__)
        if widget is None:
            widget = next(iter(self._widgets.values()))

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
            return 0

#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- Geometry wizard page
================================================================================

.. module:: geometry
   :synopsis: Geometry wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.geometry

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
from PySide.QtGui import QComboBox, QSizePolicy, QStackedWidget

# Local modules.
from pymontecarlo.ui.gui.options.wizard.options import \
    _ExpandableOptionsWizardPage

from pymontecarlo.util.parameter import expand

from pymontecarlo.options.material import Material

# Globals and constants variables.

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
            newwidget.setValue(self.options().geometry)

        self._wdg_geometry.setCurrentIndex(newindex)

        # See https://qt-project.org/faq/answer/how_can_i_get_a_qstackedwidget_to_automatically_switch_size_depending_on_th
        oldwidget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        newwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._wdg_geometry.adjustSize()

    def _find_material_class(self, programs):
        highest_class = Material

        for program in programs:
            converter = program.converter_class
            for clasz in converter.MATERIALS:
                if issubclass(clasz, highest_class):
                    highest_class = clasz

        return highest_class

    def initializePage(self):
        _ExpandableOptionsWizardPage.initializePage(self)

        # Clear
        self._widgets.clear()
        for i in reversed(range(self._cb_geometry.count())):
            self._cb_geometry.removeItem(i)
            self._wdg_geometry.removeWidget(self._wdg_geometry.widget(i))

        # Populate combo box
        it = self._iter_widgets('pymontecarlo.ui.gui.options.geometry',
                                'GEOMETRIES')
        for clasz, widget_class, programs in it:
            widget = widget_class()
            widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            widget.setMaterialClass(self._find_material_class(programs))

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
            widget = next(iter(self._widgets.values()))

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
            return 0


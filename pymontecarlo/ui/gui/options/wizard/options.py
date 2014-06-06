#!/usr/bin/env python
"""
================================================================================
:mod:`options` -- Base wizard pages
================================================================================

.. module:: options
   :synopsis: Base wizard pages

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.options

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
from operator import attrgetter

# Third party modules.
from PySide.QtGui import \
    QWizardPage, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QFrame
from PySide.QtCore import Qt, Signal

from pkg_resources import iter_entry_points

# Local modules.

# Globals and constants variables.

class SimulationCountLabel(QLabel):

    def setValue(self, value):
        if value == 0:
            text = 'No simulation defined'
        elif value > 1:
            text = '%i simulations defined' % value
        else:
            text = '%i simulation defined' % value
        QLabel.setText(self, text)

    def value(self):
        return int(QLabel.text(self).split(' ')[0])

class _OptionsWizardPage(QWizardPage):

    def __init__(self, options, parent=None):
        QWizardPage.__init__(self, parent)

        # Variables
        self._options = options

        # Layouts
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        sublayout = self._initUI() # Initialize widgets
        sublayout.setContentsMargins(10, 10, 10, 10)
        layout.addLayout(sublayout, 1)
        layout.addStretch()

        self.setLayout(layout)

    def _initUI(self):
        layout = QFormLayout()
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        return layout

    def options(self):
        return self._options

class _ExpandableOptionsWizardPage(_OptionsWizardPage):

    valueChanged = Signal()

    def __init__(self, options, parent=None):
        _OptionsWizardPage.__init__(self, options, parent)

        # Widgets
        self._lbl_count = SimulationCountLabel()
        self._lbl_count.setAlignment(Qt.AlignCenter)
        self._lbl_count.setValue(1)

        # Layouts
        layout = self.layout()

        frm_line = QFrame()
        frm_line.setFrameStyle(QFrame.HLine)
        frm_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(frm_line)

        sublayout = QHBoxLayout()
        sublayout.setContentsMargins(10, 0, 10, 0)
        sublayout.addWidget(self._lbl_count)
        layout.addLayout(sublayout)

        # Signals
        self.valueChanged.connect(self._onChanged)

    def _onChanged(self):
        pageids = set(self.wizard().visitedPages())
        pageids.add(self.wizard().currentId())

        if not pageids:
            return 0

        count = 1
        for pageid in pageids:
            page = self.wizard().page(pageid)
            if hasattr(page, 'expandCount'):
                count *= page.expandCount()

        self._lbl_count.setValue(count)

    def _iter_widgets(self, entry_point_group, converter_attr):
        allwidgets = {}
        for entry_point in iter_entry_points(entry_point_group):
            allwidgets[entry_point.name] = entry_point.load()

        widget_classes = {}
        programs = {}
        for program in self.options().programs:
            converter = program.converter_class

            for clasz in getattr(converter, converter_attr):
                name = clasz.__name__
                if name not in allwidgets:
                    continue
                widget_classes[clasz] = allwidgets[name]
                programs.setdefault(clasz, set()).add(program)

        for clasz in sorted(widget_classes.keys(), key=attrgetter('__name__')):
            yield clasz, widget_classes[clasz], programs[clasz]

    def expandCount(self):
        raise NotImplementedError

    def initializePage(self):
        self._onChanged()


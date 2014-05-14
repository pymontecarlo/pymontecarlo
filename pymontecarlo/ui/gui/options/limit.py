#!/usr/bin/env python
"""
================================================================================
:mod:`limit` -- Limit widgets
================================================================================

.. module:: limit
   :synopsis: Limit widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.options.limit

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from PySide.QtGui import QLabel, QWidget, QVBoxLayout, QTabWidget

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    _ParameterizedClassWidget, NumericalParameterWidget, TimeParameterWidget
from pymontecarlo.ui.gui.util.registry import get_widget_class as _get_widget_class

from pymontecarlo.options.limit import TimeLimit, ShowersLimit

from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

#--- Limit widgets

class _LimitWidget(_ParameterizedClassWidget):
    pass

class TimeLimitWidget(_LimitWidget):

    def __init__(self, parent=None):
        _LimitWidget.__init__(self, parent)
        self.setAccessibleName('Time')

    def _initUI(self):
        # Widgets
        self._lbl_time = QLabel('Time')
        self._lbl_time.setStyleSheet("color: blue")
        self._txt_time = TimeParameterWidget(TimeLimit.time_s)

        # Layouts
        layout = _LimitWidget._initUI(self)
        layout.addRow(self._lbl_time, self._txt_time)

        return layout

    def value(self):
        return TimeLimit(time_s=self._txt_time.values())

    def setValue(self, value):
        if hasattr(value, 'time_s'):
            self._txt_time.setValues(value.time_s)

    def setReadOnly(self, state):
        _LimitWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_time.setStyleSheet(style)

class ShowersLimitWidget(_LimitWidget):

    def __init__(self, parent=None):
        _LimitWidget.__init__(self, parent)
        self.setAccessibleName('Showers')

    def _initUI(self):
        # Widgets
        self._lbl_showers = QLabel('Number of electron showers')
        self._lbl_showers.setStyleSheet("color: blue")
        self._txt_showers = NumericalParameterWidget(ShowersLimit.showers)

        # Layouts
        layout = _LimitWidget._initUI(self)
        layout.addRow(self._lbl_showers, self._txt_showers)

        return layout

    def value(self):
        return ShowersLimit(showers=self._txt_showers.values())

    def setValue(self, value):
        if hasattr(value, 'showers'):
            self._txt_showers.setValues(value.showers)

    def setReadOnly(self, state):
        _LimitWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_showers.setStyleSheet(style)

#--- Group widgets

class LimitsWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Variables
        self._tabs = {}
        self._widgets = {}
        self._readonly = False

        # Widgets
        self._wdg_tab = QTabWidget()

        # Layouts
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._wdg_tab)
        self.setLayout(layout)

    def addLimit(self, limit):
        clasz = limit.__class__
        if clasz in self._tabs:
            raise ValueError('Limit (%s) already added' % clasz.__name__)

        wdg_limit = get_widget_class(clasz)()
        wdg_limit.setValue(limit)
        wdg_limit.setReadOnly(self._readonly)
        self._widgets[clasz] = wdg_limit

        layout = QVBoxLayout()
        layout.addWidget(wdg_limit, 1)

        widget = QWidget()
        widget.setLayout(layout)

        class_name = camelcase_to_words(clasz.__name__)
        index = self._wdg_tab.addTab(widget, class_name)
        self._tabs[clasz] = index

    def addLimits(self, limits):
        for limit in limits:
            self.addLimit(limit)

    def removeLimit(self, limit):
        clasz = limit.__class__
        index = self._tabs.pop(clasz)
        self._wdg_tab.removeTab(index)
        del self._widgets[clasz]

    def clear(self):
        self._wdg_tab.clear()
        self._tabs.clear()
        self._widgets.clear()

    def setReadOnly(self, state):
        self._readonly = state
        for widget in self._widgets.values():
            widget.setReadOnly(state)

    def isReadOnly(self):
        return self._readonly

#--- Functions

def get_widget_class(clasz):
    return _get_widget_class('pymontecarlo.ui.gui.options.limit', clasz)

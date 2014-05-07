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

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    _ParameterizedClassWidget, NumericalParameterWidget
from pymontecarlo.ui.gui.util.tango import color as c

from pymontecarlo.ui.gui.options.options import get_widget_class as _get_widget_class

from pymontecarlo.options.limit import TimeLimit, ShowersLimit

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
        self._txt_time = NumericalParameterWidget(TimeLimit.time_s)

        # Layouts
        layout = _LimitWidget._initUI(self)
        layout.addRow(c('Time', 'blue'), self._txt_time)

        return layout

    def value(self):
        return TimeLimit(time_s=self._txt_time.values())

    def setValue(self, value):
        if hasattr(value, 'time_s'):
            self._txt_time.setValues(value.time_s)

class ShowersLimitWidget(_LimitWidget):

    def __init__(self, parent=None):
        _LimitWidget.__init__(self, parent)
        self.setAccessibleName('Showers')

    def _initUI(self):
        # Widgets
        self._txt_showers = NumericalParameterWidget(ShowersLimit.showers)

        # Layouts
        layout = _LimitWidget._initUI(self)
        layout.addRow(c('Number of electron showers', 'blue'), self._txt_showers)

        return layout

    def value(self):
        return ShowersLimit(showers=self._txt_showers.values())

    def setValue(self, value):
        if hasattr(value, 'showers'):
            self._txt_showers.setValues(value.showers)

#--- Functions

def get_widget_class(clasz):
    return _get_widget_class('pymontecarlo.ui.gui.options.limit', clasz)
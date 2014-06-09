#!/usr/bin/env python
"""
================================================================================
:mod:`parameter` -- Widgets for parameters
================================================================================

.. module:: parameter
   :synopsis: Widgets for parameters

.. inheritance-diagram:: pymontecarlo.ui.gui.util.parameter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
import logging

# Third party modules.
from PySide.QtGui import \
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QValidator
from PySide.QtCore import Signal

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.widget import \
    (NumericalValidator, MultiNumericalLineEdit, UnitComboBox, AngleComboBox,
     TimeComboBox)

# Globals and constants variables.

class _ParameterWidget(QWidget):

    valuesChanged = Signal()
    validationRequested = Signal()

    def __init__(self, parameter, parent=None):
        QWidget.__init__(self, parent)
        self.setAccessibleName(parameter.name)
        self.setAccessibleDescription(parameter.__doc__.capitalize())
        self.setToolTip(parameter.__doc__.capitalize())

        self._parameter = parameter
        self._required = True

    def parameter(self):
        return self._parameter

    def values(self):
        raise NotImplementedError

    def setValues(self, values):
        raise NotImplementedError

    def isReadOnly(self):
        raise NotImplementedError

    def setReadOnly(self, state):
        raise NotImplementedError

    def isRequired(self):
        return self._required

    def setRequired(self, state):
        self._required = state
        self.validationRequested.emit()

    def hasAcceptableInput(self):
        try:
            values = self.values()
            self.parameter().validate(values)
        except Exception as ex:
            logging.error(ex)
            return False

        if self.isRequired() and len(values) == 0:
            return False

        return True

class _ParameterizedClassWidget(QWidget):

    valueChanged = Signal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Layouts
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._initUI()) # Initialize widgets
        layout.addStretch()
        self.setLayout(layout)

        # Signals
        for widget in self._iter_parameter_widgets():
            widget.valuesChanged.connect(self.valueChanged)

    def _initUI(self):
        layout = QFormLayout()
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        return layout

    def _iter_parameter_widgets(self):
        layout = self.layout().itemAt(0).layout() # FormLayout
        widgets = [layout.itemAt(i).widget() for i in range(layout.count())]
        return filter(lambda w: isinstance(w, _ParameterWidget), widgets)

    def value(self):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError

    def isReadOnly(self):
        return all(map(lambda w: w.isReadOnly(), self._iter_parameter_widgets()))

    def setReadOnly(self, state):
        for widget in self._iter_parameter_widgets():
            widget.setReadOnly(state)

    def hasAcceptableInput(self):
        return all(map(lambda w: w.hasAcceptableInput(), self._iter_parameter_widgets()))

class _ParameterValidator(NumericalValidator):

    def __init__(self, parameter):
        NumericalValidator.__init__(self)
        self._parameter = parameter

    def validate(self, values):
        try:
            self._parameter.validate(values)
        except:
            return QValidator.Intermediate

        return QValidator.Acceptable

class NumericalParameterWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._txt_values = MultiNumericalLineEdit()
        self._txt_values.setValidator(_ParameterValidator(parameter))

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_values)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_values.textChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_values.setStyleSheet("background: none")
        else:
            self._txt_values.setStyleSheet("background: pink")

    def values(self):
        return self._txt_values.values()

    def setValues(self, values):
        self._txt_values.setValues(values)

    def isReadOnly(self):
        self._txt_values.isReadOnly()

    def setReadOnly(self, state):
        self._txt_values.setReadOnly(state)

    def hasAcceptableInput(self):
        if not _ParameterWidget.hasAcceptableInput(self):
            return False
        return self._txt_values.hasAcceptableInput()

class _FactorParameterValidator(_ParameterValidator):

    def __init__(self, parameter, combobox):
        _ParameterValidator.__init__(self, parameter)
        self._combobox = combobox

    def validate(self, values):
        values *= self._combobox.factor()
        return _ParameterValidator.validate(self, values)

class UnitParameterWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._cb_unit = UnitComboBox(parameter.unit)

        self._txt_values = MultiNumericalLineEdit()
        validator = _FactorParameterValidator(parameter, self._cb_unit)
        self._txt_values.setValidator(validator)

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_values, 1)
        layout.addWidget(self._cb_unit)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_values.textChanged.connect(self.valuesChanged)
        self._cb_unit.currentIndexChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_values.setStyleSheet("background: none")
        else:
            self._txt_values.setStyleSheet("background: pink")

    def values(self):
        return self._txt_values.values() * self._cb_unit.factor()

    def setValues(self, values):
        self._txt_values.setValues(values)
        self._cb_unit.setUnit(self.parameter().unit)

    def isReadOnly(self):
        return self._txt_values.isReadOnly() and not self._cb_unit.isEnabled()

    def setReadOnly(self, state):
        self._txt_values.setReadOnly(state)
        self._cb_unit.setEnabled(not state)

    def hasAcceptableInput(self):
        if not _ParameterWidget.hasAcceptableInput(self):
            return False
        return self._txt_values.hasAcceptableInput()

class AngleParameterWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._cb_unit = AngleComboBox()
        self._cb_unit.setUnit(u'\u00b0')

        self._txt_values = MultiNumericalLineEdit()
        validator = _FactorParameterValidator(parameter, self._cb_unit)
        self._txt_values.setValidator(validator)

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_values, 1)
        layout.addWidget(self._cb_unit)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_values.textChanged.connect(self.valuesChanged)
        self._cb_unit.currentIndexChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_values.setStyleSheet("background: none")
        else:
            self._txt_values.setStyleSheet("background: pink")

    def values(self):
        return self._txt_values.values() * self._cb_unit.factor()

    def setValues(self, values):
        self._txt_values.setValues(np.degrees(values))
        self._cb_unit.setUnit(u'\u00b0')

    def isReadOnly(self):
        return self._txt_values.isReadOnly() and not self._cb_unit.isEnabled()

    def setReadOnly(self, state):
        self._txt_values.setReadOnly(state)
        self._cb_unit.setEnabled(not state)

    def hasAcceptableInput(self):
        if not _ParameterWidget.hasAcceptableInput(self):
            return False
        return self._txt_values.hasAcceptableInput()

_TimeParameterValidator = _ParameterValidator

class TimeParameterWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent=parent)

        # Widgets
        self._cb_time = TimeComboBox()

        self._txt_values = MultiNumericalLineEdit()
        validator = _FactorParameterValidator(parameter, self._cb_time)
        self._txt_values.setValidator(validator)

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_values, 1)
        layout.addWidget(self._cb_time)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_values.textChanged.connect(self.valuesChanged)
        self._cb_time.currentIndexChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_values.setStyleSheet("background: none")
        else:
            self._txt_values.setStyleSheet("background: pink")

    def values(self):
        return self._txt_values.values() * self._cb_time.factor()

    def setValues(self, values):
        self._txt_values.setValues(values)
        self._cb_time.setScale('s')

    def isReadOnly(self):
        return self._txt_values.isReadOnly() and not self._cb_time.isEnabled()

    def setReadOnly(self, state):
        self._txt_values.setReadOnly(state)
        self._cb_time.setEnabled(not state)

    def hasAcceptableInput(self):
        if not _ParameterWidget.hasAcceptableInput(self):
            return False
        return self._txt_values.hasAcceptableInput()

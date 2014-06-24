#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- Detector widgets
================================================================================

.. module:: detector
   :synopsis: module_desc

.. inheritance-diagram:: pymontecarlo.ui.gui.options.detector

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
from operator import itemgetter

# Third party modules.
from PySide.QtGui import \
    (QHBoxLayout, QLabel, QCheckBox, QWidget, QTabWidget, QVBoxLayout,
     QRadioButton, QFormLayout)
from PySide.QtCore import Qt

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    (_ParameterizedClassWidget, _ParameterWidget, NumericalParameterWidget,
     AngleParameterWidget)
from pymontecarlo.ui.gui.util.widget import \
    UnitComboBox, MultiNumericalLineEdit, AngleComboBox
from pymontecarlo.ui.gui.util.layout import merge_formlayout
from pymontecarlo.ui.gui.util.registry import get_widget_class as _get_widget_class

from pymontecarlo.options.detector import \
    (_DelimitedDetector, _ChannelsDetector, _SpatialDetector, _EnergyDetector,
     _PolarAngularDetector, _AzimuthalAngularDetector,
     BackscatteredElectronEnergyDetector, TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, TransmittedElectronPolarAngularDetector,
     BackscatteredElectronAzimuthalAngularDetector, TransmittedElectronAzimuthalAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonSpectrumDetector, PhotonDepthDetector, PhiZDetector, 
     PhotonRadialDetector, PhotonEmissionMapDetector, PhotonIntensityDetector, 
     TimeDetector, ElectronFractionDetector, ShowersStatisticsDetector, 
     TrajectoryDetector)

from pymontecarlo.util.parameter import AngleParameter, range_validator

# Globals and constants variables.
from pymontecarlo.options.detector import HALFPI, TWOPI

#--- Parameter widgets

class _AngleRangeWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._txt_lower = MultiNumericalLineEdit()
        self._txt_upper = MultiNumericalLineEdit()
        self._cb_unit = AngleComboBox()
        self._cb_unit.setUnit(u'\u00b0')

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_lower, 1)
        layout.addWidget(QLabel("-"))
        layout.addWidget(self._txt_upper, 1)
        layout.addWidget(self._cb_unit)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_lower.textChanged.connect(self.valuesChanged)
        self._txt_upper.textChanged.connect(self.valuesChanged)
        self._cb_unit.currentIndexChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_lower.setStyleSheet("background: none")
            self._txt_upper.setStyleSheet("background: none")
        else:
            self._txt_lower.setStyleSheet("background: pink")
            self._txt_upper.setStyleSheet("background: pink")

    def values(self):
        lows = self._txt_lower.values() * self._cb_unit.factor()
        ups = self._txt_upper.values() * self._cb_unit.factor()
        return list(product(lows, ups))

    def setValues(self, values):
        values = np.array(values, ndmin=1)
        self._txt_lower.setValues(list(map(np.degrees, map(itemgetter(0), values))))
        self._txt_upper.setValues(list(map(np.degrees, map(itemgetter(1), values))))
        self._cb_unit.setUnit(u'\u00b0')

    def isReadOnly(self):
        return self._txt_lower.isReadOnly() and \
            self._txt_upper.isReadOnly() and \
            not self._cb_unit.isEnabled()

    def setReadOnly(self, state):
        self._txt_lower.setReadOnly(state)
        self._txt_upper.setReadOnly(state)
        self._cb_unit.setEnabled(not state)

class _UnitRangeWidget(_ParameterWidget):

    def __init__(self, parameter, parent=None):
        _ParameterWidget.__init__(self, parameter, parent)

        # Widgets
        self._txt_lower = MultiNumericalLineEdit()
        self._txt_upper = MultiNumericalLineEdit()
        self._cb_unit = UnitComboBox(parameter.unit)

        # Layouts
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_lower, 1)
        layout.addWidget(QLabel("-"))
        layout.addWidget(self._txt_upper, 1)
        layout.addWidget(self._cb_unit)
        self.setLayout(layout)

        # Signals
        self.valuesChanged.connect(self._onChanged)
        self.validationRequested.connect(self._onChanged)

        self._txt_lower.textChanged.connect(self.valuesChanged)
        self._txt_upper.textChanged.connect(self.valuesChanged)
        self._cb_unit.currentIndexChanged.connect(self.valuesChanged)

        self.validationRequested.emit()

    def _onChanged(self):
        if self.hasAcceptableInput():
            self._txt_lower.setStyleSheet("background: none")
            self._txt_upper.setStyleSheet("background: none")
        else:
            self._txt_lower.setStyleSheet("background: pink")
            self._txt_upper.setStyleSheet("background: pink")

    def values(self):
        lows = self._txt_lower.values() * self._cb_unit.factor()
        ups = self._txt_upper.values() * self._cb_unit.factor()
        return list(product(lows, ups))

    def setValues(self, values):
        values = np.array(values, ndmin=1)
        self._txt_lower.setValues(list(map(itemgetter(0), values)))
        self._txt_upper.setValues(list(map(itemgetter(1), values)))
        self._cb_unit.setUnit(self.parameter().unit)

    def isReadOnly(self):
        return self._txt_lower.isReadOnly() and \
            self._txt_upper.isReadOnly() and \
            not self._cb_unit.isEnabled()

    def setReadOnly(self, state):
        self._txt_lower.setReadOnly(state)
        self._txt_upper.setReadOnly(state)
        self._cb_unit.setEnabled(not state)

#--- Detector widgets

class _DetectorWidget(_ParameterizedClassWidget):
    pass

class _DelimitedDetectorWidget(_DetectorWidget):

    def _initUI(self):
        # Widgets
        self._rb_delimited = QRadioButton('Delimited')
        self._rb_delimited.setChecked(False)

        self._lbl_elevation = QLabel("Elevation")
        self._lbl_elevation.setStyleSheet("color: blue")
        self._txt_elevation = _AngleRangeWidget(_DelimitedDetector.elevation_rad)
        self._txt_elevation.setEnabled(False)
        self._txt_elevation.setRequired(False)

        self._lbl_azimuth = QLabel('Azimuth')
        self._lbl_azimuth.setStyleSheet("color: blue")
        self._txt_azimuth = _AngleRangeWidget(_DelimitedDetector.azimuth_rad)
        self._txt_azimuth.setEnabled(False)
        self._txt_azimuth.setRequired(False)

        self._rb_annular = QRadioButton('Annular')
        self._rb_annular.setChecked(True)

        self._lbl_takeoffangle = QLabel('Take-off angle')
        self._lbl_takeoffangle.setStyleSheet("color: blue")
        param_takeoffangle = \
            AngleParameter(validators=range_validator(0.0, HALFPI),
                           doc='Take-off angle from the x-y plane')
        param_takeoffangle._name = 'takeoffangle'
        self._txt_takeoffangle = AngleParameterWidget(param_takeoffangle)

        self._lbl_opening = QLabel('Opening')
        self._lbl_opening.setStyleSheet("color: blue")
        param_opening = \
            AngleParameter(validators=range_validator(0.0, HALFPI, False),
                           doc='Opening angle from the take-off angle (above and below)')
        param_opening._name = 'opening'
        self._txt_opening = AngleParameterWidget(param_opening)

        # Layouts
        layout = _DetectorWidget._initUI(self)

        layout.addRow(self._rb_delimited)

        sublayout = QFormLayout()
        sublayout.setContentsMargins(10, 0, 0, 0)
        if sys.platform == 'darwin': # Fix for Mac OS
            sublayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        sublayout.addRow(self._lbl_elevation, self._txt_elevation)
        sublayout.addRow(self._lbl_azimuth, self._txt_azimuth)
        layout.addRow(sublayout)

        layout.addRow(self._rb_annular)

        sublayout = QFormLayout()
        sublayout.setContentsMargins(10, 0, 0, 0)
        if sys.platform == 'darwin': # Fix for Mac OS
            sublayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        sublayout.addRow(self._lbl_takeoffangle, self._txt_takeoffangle)
        sublayout.addRow(self._lbl_opening, self._txt_opening)
        layout.addRow(sublayout)

        # Signals
        self._rb_delimited.toggled.connect(self._onToggle)
        self._rb_annular.toggled.connect(self._onToggle)

        return layout

    def _onToggle(self):
        state = self._rb_delimited.isChecked()
        self._txt_elevation.setEnabled(state)
        self._txt_azimuth.setEnabled(state)
        self._txt_elevation.setRequired(state)
        self._txt_azimuth.setRequired(state)
        self._txt_takeoffangle.setEnabled(not state)
        self._txt_opening.setEnabled(not state)
        self._txt_takeoffangle.setRequired(not state)
        self._txt_opening.setRequired(not state)

    def _getElevationValues(self):
        if self._rb_delimited.isChecked():
            return self._txt_elevation.values()
        else:
            takeoffangles = self._txt_takeoffangle.values()
            openings = self._txt_opening.values()

            elevations = []
            for takeoffangle, opening in product(takeoffangles, openings):
                elevation = (takeoffangle - opening, takeoffangle + opening)
                elevations.append(elevation)

            return elevations

    def _getAzimuthValues(self):
        if self._rb_delimited.isChecked():
            return self._txt_azimuth.values()
        else:
            return [(0.0, TWOPI)]

    def setValue(self, value):
        self._rb_delimited.setChecked(True)
        self._txt_elevation.setValues(value.elevation_rad)
        self._txt_azimuth.setValues(value.azimuth_rad)
        self._txt_takeoffangle.setValues([])
        self._txt_opening.setValues([])

    def setReadOnly(self, state):
        _DetectorWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._rb_delimited.setEnabled(not state)
        self._rb_annular.setEnabled(not state)
        self._lbl_elevation.setStyleSheet(style)
        self._txt_elevation.setReadOnly(state)
        self._lbl_azimuth.setStyleSheet(style)
        self._txt_azimuth.setReadOnly(state)
        self._lbl_takeoffangle.setStyleSheet(style)
        self._txt_takeoffangle.setReadOnly(state)
        self._lbl_opening.setStyleSheet(style)
        self._txt_opening.setReadOnly(state)

class _ChannelsDetectorWidget(_ParameterizedClassWidget):

    def _initUI(self):
        # Widgets
        self._lbl_channels = QLabel('Channels')
        self._lbl_channels.setStyleSheet("color: blue")
        self._txt_channels = NumericalParameterWidget(_ChannelsDetector.channels)

        # Layouts
        layout = _ParameterizedClassWidget._initUI(self)
        layout.addRow(self._lbl_channels, self._txt_channels)

        return layout

    def setValue(self, value):
        self._txt_channels.setValues(value.channels)

    def setReadOnly(self, state):
        _ParameterizedClassWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_channels.setStyleSheet(style)

class _SpatialDetectorWidget(_ParameterizedClassWidget):

    def _initUI(self):
        # Widgets
        self._lbl_xlimits = QLabel('X limits')
        self._lbl_xlimits.setStyleSheet("color: blue")
        self._txt_xlimits = _UnitRangeWidget(_SpatialDetector.xlimits_m)

        self._lbl_xbins = QLabel('X bins')
        self._lbl_xbins.setStyleSheet("color: blue")
        self._txt_xbins = NumericalParameterWidget(_SpatialDetector.xbins)

        self._lbl_ylimits = QLabel('Y limits')
        self._lbl_ylimits.setStyleSheet("color: blue")
        self._txt_ylimits = _UnitRangeWidget(_SpatialDetector.ylimits_m)

        self._lbl_ybins = QLabel('Y bins')
        self._lbl_ybins.setStyleSheet("color: blue")
        self._txt_ybins = NumericalParameterWidget(_SpatialDetector.ybins)

        self._lbl_zlimits = QLabel('Z limits')
        self._lbl_zlimits.setStyleSheet("color: blue")
        self._txt_zlimits = _UnitRangeWidget(_SpatialDetector.zlimits_m)

        self._lbl_zbins = QLabel('Z bins')
        self._lbl_zbins.setStyleSheet("color: blue")
        self._txt_zbins = NumericalParameterWidget(_SpatialDetector.zbins)

        # Layouts
        layout = _ParameterizedClassWidget._initUI(self)
        layout.addRow(self._lbl_xlimits, self._txt_xlimits)
        layout.addRow(self._lbl_xbins, self._txt_xbins)
        layout.addRow(self._lbl_ylimits, self._txt_ylimits)
        layout.addRow(self._lbl_ybins, self._txt_ybins)
        layout.addRow(self._lbl_zlimits, self._txt_zlimits)
        layout.addRow(self._lbl_zbins, self._txt_zbins)

        return layout

    def setValue(self, value):
        self._txt_xlimits.setValues(value.xlimits_m)
        self._txt_xbins.setValues(value.xbins)
        self._txt_ylimits.setValues(value.ylimits_m)
        self._txt_ybins.setValues(value.ybins)
        self._txt_zlimits.setValues(value.zlimits_m)
        self._txt_zbins.setValues(value.zbins)

    def setReadOnly(self, state):
        _ParameterizedClassWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_xlimits.setStyleSheet(style)
        self._lbl_xbins.setStyleSheet(style)
        self._lbl_ylimits.setStyleSheet(style)
        self._lbl_ybins.setStyleSheet(style)
        self._lbl_zlimits.setStyleSheet(style)
        self._lbl_zbins.setStyleSheet(style)

class _EnergyDetectorWidget(_ChannelsDetectorWidget):

    def _initUI(self):
        # Widgets
        self._lbl_limits = QLabel('Limits')
        self._lbl_limits.setStyleSheet('color: blue')
        self._txt_limits = _UnitRangeWidget(_EnergyDetector.limits_eV)

        # Layouts
        layout = _ChannelsDetectorWidget._initUI(self)
        layout.addRow(self._lbl_limits, self._txt_limits)

        return layout

    def setValue(self, value):
        _ChannelsDetectorWidget.setValue(self, value)
        self._txt_limits.setValues(value.limits_eV)

    def setReadOnly(self, state):
        _ChannelsDetectorWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_limits.setStyleSheet(style)

class _AngularDetectorWidget(_ChannelsDetectorWidget):
    pass

class _PolarAngularDetectorWidget(_AngularDetectorWidget):

    def _initUI(self):
        # Widgets
        self._lbl_limits = QLabel('Limits')
        self._lbl_limits.setStyleSheet('color: blue')
        self._txt_limits = _AngleRangeWidget(_PolarAngularDetector.limits_rad)
        self._txt_limits.setValues([(-HALFPI, HALFPI)])

        # Layouts
        layout = _AngularDetectorWidget._initUI(self)
        layout.addRow(self._lbl_limits, self._txt_limits)

        return layout

    def setValue(self, value):
        _AngularDetectorWidget.setValue(self, value)
        self._txt_limits.setValues(value.limits_rad)

    def setReadOnly(self, state):
        _AngularDetectorWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_limits.setStyleSheet(style)

class _AzimuthalAngularDetectorWidget(_AngularDetectorWidget):

    def _initUI(self):
        # Widgets
        self._lbl_limits = QLabel('Limits')
        self._lbl_limits.setStyleSheet('color: blue')
        self._txt_limits = _AngleRangeWidget(_AzimuthalAngularDetector.limits_rad)
        self._txt_limits.setValues([(0, TWOPI)])

        # Layouts
        layout = _AngularDetectorWidget._initUI(self)
        layout.addRow(self._lbl_limits, self._txt_limits)

        return layout

    def setValue(self, value):
        _AngularDetectorWidget.setValue(self, value)
        self._txt_limits.setValues(value.limits_rad)

    def setReadOnly(self, state):
        _AngularDetectorWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_limits.setStyleSheet(style)

class _PhotonDelimitedDetectorWidget(_DelimitedDetectorWidget):
    pass

class BackscatteredElectronEnergyDetectorWidget(_EnergyDetectorWidget):

    def __init__(self, parent=None):
        _EnergyDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Backscattered electron energy")

    def value(self):
        channels = self._txt_channels.values()
        limits_eV = self._txt_limits.values()
        return BackscatteredElectronEnergyDetector(channels, limits_eV)

class TransmittedElectronEnergyDetectorWidget(_EnergyDetectorWidget):

    def __init__(self, parent=None):
        _EnergyDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Transmitted electron energy")

    def value(self):
        channels = self._txt_channels.values()
        limits_eV = self._txt_limits.values()
        return TransmittedElectronEnergyDetector(channels, limits_eV)

class BackscatteredElectronPolarAngularDetectorWidget(_PolarAngularDetectorWidget):

    def __init__(self, parent=None):
        _PolarAngularDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Backscattered electron polar angular")

    def value(self):
        channels = self._txt_channels.values()
        limits_rad = self._txt_limits.values()
        return BackscatteredElectronPolarAngularDetector(channels, limits_rad)

class TransmittedElectronPolarAngularDetectorWidget(_PolarAngularDetectorWidget):

    def __init__(self, parent=None):
        _PolarAngularDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Transmitted electron polar angular")

    def value(self):
        channels = self._txt_channels.values()
        limits_rad = self._txt_limits.values()
        return TransmittedElectronPolarAngularDetector(channels, limits_rad)

class BackscatteredElectronAzimuthalAngularDetectorWidget(_AzimuthalAngularDetectorWidget):

    def __init__(self, parent=None):
        _AzimuthalAngularDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Backscattered electron azimuthal angular")

    def value(self):
        channels = self._txt_channels.values()
        limits_rad = self._txt_limits.values()
        return BackscatteredElectronAzimuthalAngularDetector(channels, limits_rad)

class TransmittedElectronAzimuthalAngularDetectorWidget(_AzimuthalAngularDetectorWidget):

    def __init__(self, parent=None):
        _AzimuthalAngularDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Transmitted electron azimuthal angular")

    def value(self):
        channels = self._txt_channels.values()
        limits_rad = self._txt_limits.values()
        return TransmittedElectronAzimuthalAngularDetector(channels, limits_rad)

class BackscatteredElectronRadialDetectorWidget(_ChannelsDetectorWidget):

    def __init__(self, parent=None):
        _ChannelsDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Backscattered electron radial")

    def value(self):
        channels = self._txt_channels.values()
        return BackscatteredElectronRadialDetector(channels)

class PhotonSpectrumDetectorWidget(_PhotonDelimitedDetectorWidget,
                                   _EnergyDetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon spectrum")

    def _initUI(self):
        layout1 = _PhotonDelimitedDetectorWidget._initUI(self)
        layout2 = _EnergyDetectorWidget._initUI(self)
        return merge_formlayout(layout1, layout2)

    def value(self):
        elevation_rad = self._getElevationValues()
        azimuth_rad = self._getAzimuthValues()
        channels = self._txt_channels.values()
        limits_eV = self._txt_limits.values()
        return PhotonSpectrumDetector(elevation_rad, azimuth_rad,
                                      channels, limits_eV)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        _EnergyDetectorWidget.setValue(self, value)

    def setReadOnly(self, state):
        _PhotonDelimitedDetectorWidget.setReadOnly(self, state)
        _EnergyDetectorWidget.setReadOnly(self, state)

class PhotonDepthDetectorWidget(_PhotonDelimitedDetectorWidget,
                                _ChannelsDetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon depth")

    def _initUI(self):
        layout1 = _PhotonDelimitedDetectorWidget._initUI(self)
        layout2 = _ChannelsDetectorWidget._initUI(self)
        return merge_formlayout(layout1, layout2)

    def value(self):
        elevation_rad = self._getElevationValues()
        azimuth_rad = self._getAzimuthValues()
        channels = self._txt_channels.values()
        return PhotonDepthDetector(elevation_rad, azimuth_rad, channels)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        _ChannelsDetectorWidget.setValue(self, value)

    def setReadOnly(self, state):
        _PhotonDelimitedDetectorWidget.setReadOnly(self, state)
        _ChannelsDetectorWidget.setReadOnly(self, state)

class PhiZDetectorWidget(_PhotonDelimitedDetectorWidget,
                            _ChannelsDetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Phi-z")

    def _initUI(self):
        layout1 = _PhotonDelimitedDetectorWidget._initUI(self)
        layout2 = _ChannelsDetectorWidget._initUI(self)
        return merge_formlayout(layout1, layout2)

    def value(self):
        elevation_rad = self._getElevationValues()
        azimuth_rad = self._getAzimuthValues()
        channels = self._txt_channels.values()
        return PhiZDetector(elevation_rad, azimuth_rad, channels)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        _ChannelsDetectorWidget.setValue(self, value)

    def setReadOnly(self, state):
        _PhotonDelimitedDetectorWidget.setReadOnly(self, state)
        _ChannelsDetectorWidget.setReadOnly(self, state)

class PhotonRadialDetectorWidget(_PhotonDelimitedDetectorWidget,
                                 _ChannelsDetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon radial")

    def _initUI(self):
        layout1 = _PhotonDelimitedDetectorWidget._initUI(self)
        layout2 = _ChannelsDetectorWidget._initUI(self)
        return merge_formlayout(layout1, layout2)

    def value(self):
        elevation_rad = self._getElevationValues()
        azimuth_rad = self._getAzimuthValues()
        channels = self._txt_channels.values()
        return PhotonRadialDetector(elevation_rad, azimuth_rad, channels)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        _ChannelsDetectorWidget.setValue(self, value)

    def setReadOnly(self, state):
        _PhotonDelimitedDetectorWidget.setReadOnly(self, state)
        _ChannelsDetectorWidget.setReadOnly(self, state)

class PhotonEmissionMapDetectorWidget(_PhotonDelimitedDetectorWidget):

    def __init__(self, parent=None):
        _PhotonDelimitedDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon emission map")

    def _initUI(self):
        # Widgets
        self._lbl_xbins = QLabel('X bins')
        self._lbl_xbins.setStyleSheet("color: blue")
        self._txt_xbins = NumericalParameterWidget(PhotonEmissionMapDetector.xbins)

        self._lbl_ybins = QLabel('Y bins')
        self._lbl_ybins.setStyleSheet("color: blue")
        self._txt_ybins = NumericalParameterWidget(PhotonEmissionMapDetector.ybins)

        self._lbl_zbins = QLabel('Z bins')
        self._lbl_zbins.setStyleSheet("color: blue")
        self._txt_zbins = NumericalParameterWidget(PhotonEmissionMapDetector.zbins)

        # Layouts
        layout = _PhotonDelimitedDetectorWidget._initUI(self)
        layout.addRow(self._lbl_xbins, self._txt_xbins)
        layout.addRow(self._lbl_ybins, self._txt_ybins)
        layout.addRow(self._lbl_zbins, self._txt_zbins)

        return layout

    def value(self):
        elevation_rad = self._getElevationValues()
        azimuth_rad = self._getAzimuthValues()
        xbins = self._txt_xbins.values()
        ybins = self._txt_ybins.values()
        zbins = self._txt_zbins.values()
        return PhotonEmissionMapDetector(elevation_rad, azimuth_rad,
                                         xbins, ybins, zbins)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        self._txt_xbins.setValues(value.xbins)
        self._txt_ybins.setValues(value.ybins)
        self._txt_zbins.setValues(value.zbins)

    def setReadOnly(self, state):
        _PhotonDelimitedDetectorWidget.setReadOnly(self, state)
        style = 'color: none' if state else 'color: blue'
        self._lbl_xbins.setStyleSheet(style)
        self._lbl_ybins.setStyleSheet(style)
        self._lbl_zbins.setStyleSheet(style)

class PhotonIntensityDetectorWidget(_PhotonDelimitedDetectorWidget):

    def __init__(self, parent=None):
        _PhotonDelimitedDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon intensity")

    def value(self):
        elevation_rad = self._getElevationValues()
        azimuth_rad = self._getAzimuthValues()
        return PhotonIntensityDetector(elevation_rad, azimuth_rad)

class TimeDetectorWidget(_DetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Time")

    def value(self):
        return TimeDetector()

    def setValue(self, value):
        pass

class ElectronFractionDetectorWidget(_DetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Electron fraction")

    def value(self):
        return ElectronFractionDetector()

    def setValue(self, value):
        pass

class ShowersStatisticsDetectorWidget(_DetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Showers statistics")

    def value(self):
        return ShowersStatisticsDetector()

    def setValue(self, value):
        pass

class TrajectoryDetectorWidget(_DetectorWidget):

    def __init__(self, parent=None):
        _DetectorWidget.__init__(self, parent)
        self.setAccessibleName("Trajectory")

    def _initUI(self):
        # Widgets
        self._chk_secondary = QCheckBox("Simulation secondary electrons")
        self._chk_secondary.setChecked(True)

        # Layouts
        layout = _DetectorWidget._initUI(self)
        layout.addRow(self._chk_secondary)

        return layout

    def value(self):
        secondary = self._chk_secondary.isChecked()
        return TrajectoryDetector(secondary)

    def setValue(self, value):
        self._chk_secondary.setChecked(value.secondary)

#--- Group widgets

class DetectorsWidget(QWidget):

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

    def addDetector(self, key, detector):
        if key in self._tabs:
            raise ValueError('Detector with key %s already added' % key)

        clasz = detector.__class__
        wdg_detector = get_widget_class(clasz)()
        wdg_detector.setValue(detector)
        wdg_detector.setReadOnly(self._readonly)
        self._widgets[key] = wdg_detector

        lbl_class = QLabel(clasz.__name__)
        lbl_class.setAlignment(Qt.AlignRight)
        font = lbl_class.font()
        font.setItalic(True)
        lbl_class.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(lbl_class)
        layout.addWidget(wdg_detector, 1)

        widget = QWidget()
        widget.setLayout(layout)
        index = self._wdg_tab.addTab(widget, key)
        self._tabs[key] = index

    def addDetectors(self, detectors):
        for key in sorted(detectors.keys()):
            self.addDetector(key, detectors[key])

    def removeDetector(self, key):
        index = self._tabs.pop(key)
        self._wdg_tab.removeTab(index)
        del self._widgets[key]

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
    return _get_widget_class('pymontecarlo.ui.gui.options.detector', clasz)

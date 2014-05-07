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
from itertools import product
from operator import itemgetter

# Third party modules.
from PySide.QtGui import QHBoxLayout, QLabel, QCheckBox

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    _ParameterizedClassWidget, _ParameterWidget, NumericalParameterWidget
from pymontecarlo.ui.gui.util.widget import \
    UnitComboBox, MultiNumericalLineEdit, AngleComboBox
from pymontecarlo.ui.gui.util.tango import color as c
from pymontecarlo.ui.gui.util.layout import merge_formlayout

from pymontecarlo.ui.gui.options.options import get_widget_class as _get_widget_class

from pymontecarlo.options.detector import \
    (_DelimitedDetector, _ChannelsDetector, _SpatialDetector, _EnergyDetector,
     _PolarAngularDetector, _AzimuthalAngularDetector,
     BackscatteredElectronEnergyDetector, TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, TransmittedElectronPolarAngularDetector,
     BackscatteredElectronAzimuthalAngularDetector, TransmittedElectronAzimuthalAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonPolarAngularDetector, PhotonAzimuthalAngularDetector,
     PhotonSpectrumDetector, PhotonDepthDetector, PhotonRadialDetector,
     PhotonEmissionMapDetector, PhotonIntensityDetector, TimeDetector,
     ElectronFractionDetector, ShowersStatisticsDetector, TrajectoryDetector)

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
        self._cb_unit.setUnit('rad')

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
        self._txt_elevation = _AngleRangeWidget(_DelimitedDetector.elevation_rad)
        self._txt_azimuth = _AngleRangeWidget(_DelimitedDetector.azimuth_rad)

        # Layouts
        layout = _DetectorWidget._initUI(self)
        layout.addRow(c('Elevation', 'blue'), self._txt_elevation)
        layout.addRow(c('Azimuth', 'blue'), self._txt_azimuth)

        return layout

    def setValue(self, value):
        self._txt_elevation.setValues(value.elevation_rad)
        self._txt_azimuth.setValues(value.azimuth_rad)

class _ChannelsDetectorWidget(_ParameterizedClassWidget):

    def _initUI(self):
        # Widgets
        self._txt_channels = NumericalParameterWidget(_ChannelsDetector.channels)

        # Layouts
        layout = _ParameterizedClassWidget._initUI(self)
        layout.addRow(c('Channels', 'blue'), self._txt_channels)

        return layout

    def setValue(self, value):
        self._txt_channels.setValues(value.channels)

class _SpatialDetectorWidget(_ParameterizedClassWidget):

    def _initUI(self):
        # Widgets
        self._txt_xlimits = _UnitRangeWidget(_SpatialDetector.xlimits_m)
        self._txt_xbins = NumericalParameterWidget(_SpatialDetector.xbins)
        self._txt_ylimits = _UnitRangeWidget(_SpatialDetector.ylimits_m)
        self._txt_ybins = NumericalParameterWidget(_SpatialDetector.ybins)
        self._txt_zlimits = _UnitRangeWidget(_SpatialDetector.zlimits_m)
        self._txt_zbins = NumericalParameterWidget(_SpatialDetector.zbins)

        # Layouts
        layout = _ParameterizedClassWidget._initUI(self)
        layout.addRow(c("X limits", "blue"), self._txt_xlimits)
        layout.addRow(c("X bins", "blue"), self._txt_xbins)
        layout.addRow(c("Y limits", "blue"), self._txt_ylimits)
        layout.addRow(c("Y bins", "blue"), self._txt_ybins)
        layout.addRow(c("Z limits", "blue"), self._txt_zlimits)
        layout.addRow(c("Z bins", "blue"), self._txt_zbins)

        return layout

    def setValue(self, value):
        self._txt_xlimits.setValues(value.xlimits_m)
        self._txt_xbins.setValues(value.xbins)
        self._txt_ylimits.setValues(value.ylimits_m)
        self._txt_ybins.setValues(value.ybins)
        self._txt_zlimits.setValues(value.zlimits_m)
        self._txt_zbins.setValues(value.zbins)

class _EnergyDetectorWidget(_ChannelsDetectorWidget):

    def _initUI(self):
        # Widgets
        self._txt_limits = _UnitRangeWidget(_EnergyDetector.limits_eV)

        # Layouts
        layout = _ChannelsDetectorWidget._initUI(self)
        layout.addRow(c('Limits', 'blue'), self._txt_limits)

        return layout

    def setValue(self, value):
        _ChannelsDetectorWidget.setValue(self, value)
        self._txt_limits.setValues(value.limits_eV)

class _AngularDetectorWidget(_ChannelsDetectorWidget):
    pass

class _PolarAngularDetectorWidget(_AngularDetectorWidget):

    def _initUI(self):
        # Widgets
        self._txt_limits = _AngleRangeWidget(_PolarAngularDetector.limits_rad)
        self._txt_limits.setValues([(-HALFPI, HALFPI)])

        # Layouts
        layout = _AngularDetectorWidget._initUI(self)
        layout.addRow(c("Limits", 'blue'), self._txt_limits)

        return layout

    def setValue(self, value):
        _AngularDetectorWidget.setValue(self, value)
        self._txt_limits.setValues(value.limits_rad)

class _AzimuthalAngularDetectorWidget(_AngularDetectorWidget):

    def _initUI(self):
        # Widgets
        self._txt_limits = _AngleRangeWidget(_AzimuthalAngularDetector.limits_rad)
        self._txt_limits.setValues([(0, TWOPI)])

        # Layouts
        layout = _AngularDetectorWidget._initUI(self)
        layout.addRow(c("Limits", 'blue'), self._txt_limits)

        return layout

    def setValue(self, value):
        _AngularDetectorWidget.setValue(self, value)
        self._txt_limits.setValues(value.limits_rad)

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

class PhotonPolarAngularDetectorWidget(_PolarAngularDetectorWidget):

    def __init__(self, parent=None):
        _PolarAngularDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon polar angular")

    def value(self):
        channels = self._txt_channels.values()
        limits_rad = self._txt_limits.values()
        return PhotonPolarAngularDetector(channels, limits_rad)

class PhotonAzimuthalAngularDetectorWidget(_AzimuthalAngularDetectorWidget):

    def __init__(self, parent=None):
        _AzimuthalAngularDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon azimuthal angular")

    def value(self):
        channels = self._txt_channels.values()
        limits_rad = self._txt_limits.values()
        return PhotonAzimuthalAngularDetector(channels, limits_rad)

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
        elevation_rad = self._txt_elevation.values()
        azimuth_rad = self._txt_azimuth.values()
        channels = self._txt_channels.values()
        limits_eV = self._txt_limits.values()
        return PhotonSpectrumDetector(elevation_rad, azimuth_rad,
                                      channels, limits_eV)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        _EnergyDetectorWidget.setValue(self, value)

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
        elevation_rad = self._txt_elevation.values()
        azimuth_rad = self._txt_azimuth.values()
        channels = self._txt_channels.values()
        return PhotonDepthDetector(elevation_rad, azimuth_rad, channels)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        _ChannelsDetectorWidget.setValue(self, value)

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
        elevation_rad = self._txt_elevation.values()
        azimuth_rad = self._txt_azimuth.values()
        channels = self._txt_channels.values()
        return PhotonRadialDetector(elevation_rad, azimuth_rad, channels)

    def setValue(self, value):
        _PhotonDelimitedDetectorWidget.setValue(self, value)
        _ChannelsDetectorWidget.setValue(self, value)

class PhotonEmissionMapDetectorWidget(_PhotonDelimitedDetectorWidget):

    def __init__(self, parent=None):
        _PhotonDelimitedDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon emission map")

    def _initUI(self):
        # Widgets
        self._txt_xbins = NumericalParameterWidget(PhotonEmissionMapDetector.xbins)
        self._txt_ybins = NumericalParameterWidget(PhotonEmissionMapDetector.ybins)
        self._txt_zbins = NumericalParameterWidget(PhotonEmissionMapDetector.zbins)

        # Layouts
        layout = _PhotonDelimitedDetectorWidget._initUI(self)
        layout.addRow(c('X bins', 'blue'), self._txt_xbins)
        layout.addRow(c('Y bins', 'blue'), self._txt_ybins)
        layout.addRow(c('Z bins', 'blue'), self._txt_zbins)

        return layout

    def value(self):
        elevation_rad = self._txt_elevation.values()
        azimuth_rad = self._txt_azimuth.values()
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

class PhotonIntensityDetectorWidget(_PhotonDelimitedDetectorWidget):

    def __init__(self, parent=None):
        _PhotonDelimitedDetectorWidget.__init__(self, parent)
        self.setAccessibleName("Photon intensity")

    def value(self):
        elevation_rad = self._txt_elevation.values()
        azimuth_rad = self._txt_azimuth.values()
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

#--- Functions

def get_widget_class(clasz):
    return _get_widget_class('pymontecarlo.ui.gui.options.detector', clasz)
#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- Detector widgets
================================================================================

.. module:: detector
   :synopsis: Detector widgets

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
from operator import itemgetter, attrgetter, methodcaller

# Third party modules.
from PySide.QtGui import \
    (QHBoxLayout, QLabel, QCheckBox, QComboBox, QTableView, QToolBar,
     QPushButton, QItemDelegate, QLineEdit, QRegExpValidator, QWidget,
     QSizePolicy, QMessageBox, QHeaderView, QDialog, QFormLayout,
     QDialogButtonBox)
from PySide.QtCore import \
    Qt, QAbstractTableModel, QModelIndex, QRegExp, QAbstractListModel

import numpy as np

# Local modules.
from pymontecarlo.ui.gui.util.parameter import \
    _ParameterizedClassWidget, _ParameterWidget, NumericalParameterWidget
from pymontecarlo.ui.gui.util.widget import \
    UnitComboBox, MultiNumericalLineEdit, AngleComboBox
from pymontecarlo.ui.gui.util.tango import color as c, getIcon
from pymontecarlo.ui.gui.util.layout import merge_formlayout
from pymontecarlo.ui.gui.options.options import _ExpandableOptionsWizardPage

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

from pymontecarlo.util.parameter import expand

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

#--- Wizard page

class _DetectorDialog(QDialog):

    def __init__(self, wdg_detector, key='', parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(wdg_detector.accessibleName())

        # Widgets
        self._txt_key = QLineEdit()
        self._txt_key.setValidator(QRegExpValidator(QRegExp(r"^(?!\s*$).+")))
        self._txt_key.setText(key)

        self._wdg_detector = wdg_detector

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layouts
        layout = QFormLayout()
        layout.addRow('Key', self._txt_key)
        layout.addRow(self._wdg_detector)
        layout.addRow(buttons)
        self.setLayout(layout)

        # Signals
        self._txt_key.textChanged.connect(self._onChanged)
        self._txt_key.textChanged.emit('')

        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self.reject)

    def _onChanged(self):
        if self._txt_key.hasAcceptableInput():
            self._txt_key.setStyleSheet("background: none")
        else:
            self._txt_key.setStyleSheet("background: pink")

    def _onOk(self):
        if not self._txt_key.hasAcceptableInput():
            return
        if not self._wdg_detector.hasAcceptableInput():
            return
        self.accept()

    def key(self):
        return self._txt_key.text()

    def detector(self):
        return self._wdg_detector.value()

class DetectorWizardPage(_ExpandableOptionsWizardPage):

    class _DetectorComboBoxModel(QAbstractListModel):

        def __init__(self):
            QAbstractListModel.__init__(self)
            self._detectors = []

        def rowCount(self, *args, **kwargs):
            return len(self._detectors)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < self.rowCount()):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            return self._detectors[index.row()]['text']

        def setData(self, index, value, role=Qt.EditRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._detectors)):
                return False

            row = index.row()
            self._detectors[row] = value

            self.dataChanged.emit(index, index)
            return True

        def insertRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginInsertRows(QModelIndex(), row, row + count - 1)

            for _ in range(count):
                value = {'text': '', 'class': None, 'widget_class': None}
                self._detectors.insert(row, value)

            self.endInsertRows()
            return True

        def removeRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginRemoveRows(QModelIndex(), row, row + count - 1)

            for index in reversed(range(row, row + count)):
                self._detectors.pop(index)

            self.endRemoveRows()
            return True

        def append(self, text, clasz, widget_class):
            self.insert(self.rowCount(), text, clasz, widget_class)

        def insert(self, row, text, clasz, widget_class):
            self.insertRows(row)
            value = {'text': text, 'class': clasz, 'widget_class': widget_class}
            self.setData(self.createIndex(row, 0), value)

        def clear(self):
            self.removeRows(0, self.rowCount())

        def widget_class(self, index):
            return self._detectors[index]['widget_class']

    class _DetectorTableModel(QAbstractTableModel):

        def __init__(self):
            QAbstractTableModel.__init__(self)
            self._detectors = []

        def rowCount(self, *args, **kwargs):
            return len(self._detectors)

        def columnCount(self, *args, **kwargs):
            return 2

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._detectors)):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            key, detector = self._detectors[index.row()]
            column = index.column()
            if column == 0:
                return key
            elif column == 1:
                return str(detector) if detector is not None else ''

        def headerData(self, section , orientation, role):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Horizontal:
                if section == 0:
                    return 'Key'
                elif section == 1:
                    return 'Detector'
            elif orientation == Qt.Vertical:
                return str(section + 1)

        def flags(self, index):
            if not index.isValid():
                return Qt.ItemIsEnabled

            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                Qt.ItemIsEditable)

        def setData(self, index, value, role=Qt.EditRole):
            if not index.isValid() or \
                    not (0 <= index.row() < len(self._detectors)):
                return False

            row = index.row()
            column = index.column()
            self._detectors[row][column] = value

            self.dataChanged.emit(index, index)
            return True

        def insertRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginInsertRows(parent, row, row + count - 1)

            for _ in range(count):
                self._detectors.insert(row, ['untitled', None])

            self.endInsertRows()
            return True

        def removeRows(self, row, count=1, parent=None):
            if count == 0:
                return False
            if parent is None:
                parent = QModelIndex()
            self.beginRemoveRows(parent, row, row + count - 1)

            for index in reversed(range(row, row + count)):
                self._detectors.pop(index)

            self.endRemoveRows()
            return True

        def append(self, key, detector):
            self.insert(self.rowCount(), key, detector)

        def insert(self, index, key, detector):
            self.insertRows(index)
            self.setData(self.createIndex(index, 0), key)
            self.setData(self.createIndex(index, 1), detector)

        def modify(self, index, key, detector):
            self.setData(self.createIndex(index, 0), key)
            self.setData(self.createIndex(index, 1), detector)

        def clear(self):
            self.removeRows(0, self.rowCount())

        def detectors(self):
            detectors = {}
            for key, detector in self._detectors:
                if detector is not None:
                    detectors.setdefault(key, []).append(detector)
            return detectors

        def detector(self, index):
            return self._detectors[index.row()][1]

        def key(self, index):
            return self._detectors[index.row()][0]

    class _DetectorTableDelegate(QItemDelegate):

        def __init__(self, parent=None):
            QItemDelegate.__init__(self, parent)

        def createEditor(self, parent, option, index):
            column = index.column()
            if column == 0:
                editor = QLineEdit(parent)
                editor.setValidator(QRegExpValidator(QRegExp(r"^(?!\s*$).+")))
                return editor
            elif column == 1:
                return None

        def setEditorData(self, editor, index):
            column = index.column()
            if column == 0:
                key = index.model().data(index, Qt.DisplayRole)
                editor.setText(key)

        def setModelData(self, editor, model, index):
            column = index.column()
            if column == 0:
                if not editor.hasAcceptableInput():
                    return
                model.setData(index, editor.text())

    def __init__(self, options, parent=None):
        _ExpandableOptionsWizardPage.__init__(self, options, parent)
        self.setTitle('Detector')

    def _initUI(self):
        # Variables
        self._widgets = {}
        tbl_model = self._DetectorTableModel()

        # Widgets
        self._cb_detector = QComboBox()
        self._cb_detector.setModel(self._DetectorComboBoxModel())

        btn_detector_add = QPushButton()
        btn_detector_add.setIcon(getIcon("list-add"))

        self._tbl_detector = QTableView()
        self._tbl_detector.setModel(tbl_model)
        self._tbl_detector.setItemDelegate(self._DetectorTableDelegate())
        header = self._tbl_detector.horizontalHeader()
        header.setResizeMode(1, QHeaderView.Stretch)
        policy = self._tbl_detector.sizePolicy()
        policy.setVerticalStretch(True)
        self._tbl_detector.setSizePolicy(policy)

        tlb_detector = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tlb_detector.addWidget(spacer)
        act_remove = tlb_detector.addAction(getIcon("list-remove"), "Remove detector")

        # Layouts
        layout = _ExpandableOptionsWizardPage._initUI(self)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self._cb_detector, 1)
        sublayout.addWidget(btn_detector_add)
        layout.addRow("Select", sublayout)

        layout.addRow(self._tbl_detector)
        layout.addRow(tlb_detector)

        # Signals
        btn_detector_add.released.connect(self._onDetectorAdd)
        act_remove.triggered.connect(self._onDetectorRemove)

        self._tbl_detector.doubleClicked.connect(self._onDetectorDoubleClicked)

        tbl_model.dataChanged.connect(self.valueChanged)
        tbl_model.rowsInserted.connect(self.valueChanged)
        tbl_model.rowsRemoved.connect(self.valueChanged)

        return layout

    def _onDetectorAdd(self):
        index = self._tbl_detector.selectionModel().currentIndex()
        tbl_model = self._tbl_detector.model()
        cb_model = self._cb_detector.model()

        widget_class = cb_model.widget_class(self._cb_detector.currentIndex())
        wdg_detector = widget_class()

        dialog = _DetectorDialog(wdg_detector)
        if not dialog.exec_():
            return

        tbl_model.insert(index.row() + 1, dialog.key(), dialog.detector())

    def _onDetectorRemove(self):
        selection = self._tbl_detector.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Detector", "Select a row")
            return

        tbl_model = self._tbl_detector.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            tbl_model.removeRow(row)

    def _onDetectorDoubleClicked(self, index):
        if index.column() != 1:
            return

        tbl_model = self._tbl_detector.model()
        key = tbl_model.key(index)
        detector = tbl_model.detector(index)
        widget_class = self._widgets[detector.__class__]
        wdg_detector = widget_class()
        wdg_detector.setValue(detector)

        dialog = _DetectorDialog(wdg_detector, key)
        if not dialog.exec_():
            return

        tbl_model.modify(index.row(), dialog.key(), dialog.detector())

    def initializePage(self):
        tbl_model = self._tbl_detector.model()
        cb_model = self._cb_detector.model()

        # Clear
        self._widgets.clear()
        tbl_model.clear()
        cb_model.clear()

        # Populate combo box
        it = self._iter_widgets('pymontecarlo.ui.gui.options.detector',
                                'DETECTORS')
        for clasz, widget_class, programs in it:
            widget = widget_class()
            self._widgets[clasz] = widget_class

            program_text = ', '.join(map(attrgetter('name'), programs))
            text = '{0} ({1})'.format(widget.accessibleName(), program_text)

            cb_model.append(text, clasz, widget_class)

            del widget

        self._cb_detector.setCurrentIndex(0)

        # Add detector(s)
        for key, detectors in self.options().detectors.items():
            detectors = np.array(detectors, ndmin=1)
            for detector in detectors:
                tbl_model.append(key, detector)

    def validatePage(self):
        tbl_model = self._tbl_detector.model()
        if tbl_model.rowCount() == 0:
            return False

        self.options().detectors.clear()
        self.options().detectors.update(tbl_model.detectors())

        return True

    def expandCount(self):
        try:
            count = 1

            for detectors in self._tbl_detector.model().detectors().values():
                count *= len(detectors)
                for detector in detectors:
                    count *= len(expand(detector))

            return count
        except:
            return 1

def __run():
    import sys
    from PySide.QtGui import QApplication, QMainWindow

    app = QApplication(sys.argv)
    window = QMainWindow(None)

    widget = TrajectoryDetectorWidget()

    window.setCentralWidget(widget)
    window.show()
    app.exec_()

    print(widget.hasAcceptableInput(), widget.value())

if __name__ == '__main__':
    __run()

#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- Result widgets
================================================================================

.. module:: result
   :synopsis: Result widgets

.. inheritance-diagram:: pymontecarlo.ui.gui.results.result

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys

# Third party modules.
from PySide.QtGui import \
    (QLabel, QVBoxLayout, QCheckBox, QComboBox, QFormLayout,
     QGroupBox, QTableView, QHeaderView, QLineEdit)
from PySide.QtCore import Qt, QAbstractTableModel, QAbstractListModel

import numpy as np

import matplotlib
from matplotlib.figure import Figure

# Local modules.
from pymontecarlo.util.human import camelcase_to_words, human_time
import pymontecarlo.util.physics as physics

from pymontecarlo.ui.gui.util.registry import get_widget_class as _get_widget_class

from pymontecarlo.ui.gui.results.results import \
    _BaseResultToolItem, _BaseResultWidget, _SaveableResultMixin, _FigureResultMixin
from pymontecarlo.ui.gui.options.detector import \
    get_widget_class as get_detector_widget_class

# Globals and constants variables.

#--- Base widgets

class _ResultToolItem(_BaseResultToolItem):

    def __init__(self, parent):
        self._key = parent.key()
        self._result = parent.result()

        _BaseResultToolItem.__init__(self, parent)

    def key(self):
        return self._key

    def result(self):
        return self._result

class DetectorToolItem(_ResultToolItem):

    def _initUI(self):
        # Widgets
        detector = self.options().detectors[self.key()]
        wdg_detector = get_detector_widget_class(detector.__class__)()
        wdg_detector.setValue(detector)
        wdg_detector.setReadOnly(True)

        # Layouts
        layout = _ResultToolItem._initUI(self)
        layout.addRow(wdg_detector)

        return layout

class _ResultWidget(_BaseResultWidget):

    def __init__(self, key, result, options, parent=None):
        self._key = key
        self._result = result

        _BaseResultWidget.__init__(self, options, parent)
        self.setTitle(key)
        self.setSubTitle(camelcase_to_words(result.__class__.__name__[:-6]))

    def key(self):
        return self._key

    def result(self):
        return self._result

class UnknownResultWidget(_ResultWidget):

    def _initUI(self):
        # Controls
        lbl_unknown = QLabel('No viewer for this result')
        lbl_unknown.setAlignment(Qt.AlignCenter)

        # Layouts
        layout = _ResultWidget._initUI(self)
        layout.addWidget(lbl_unknown)

        return layout

class _SaveableResultWidget(_SaveableResultMixin, _ResultWidget):

    def __init__(self, key, result, options, parent=None):
        _SaveableResultMixin.__init__(self)
        _ResultWidget.__init__(self, key, result, options, parent)

class _FigureResultWidget(_FigureResultMixin, _SaveableResultWidget):

    def __init__(self, key, result, options, parent=None):
        _FigureResultMixin.__init__(self)
        _SaveableResultWidget.__init__(self, key, result, options, parent)
        self._drawFigure()

#--- Result widgets

class _PhotonSpectrumResultOptionsToolItem(_ResultToolItem):

    def _initUI(self):
        # Widgets
        self._chk_total = QCheckBox("Show total intensity")
        self._chk_total.setChecked(True)

        self._chk_background = QCheckBox("Show background intensity")
        self._chk_background.setChecked(False)

        self._chk_errorbar = QCheckBox("Show error bars")
        self._chk_errorbar.setChecked(True)

        # Layouts
        layout = _ResultToolItem._initUI(self)
        layout.addRow(self._chk_total)
        layout.addRow(self._chk_background)
        layout.addRow(self._chk_errorbar)

        # Signals
        self._chk_total.stateChanged.connect(self.stateChanged)
        self._chk_background.stateChanged.connect(self.stateChanged)
        self._chk_errorbar.stateChanged.connect(self.stateChanged)

        return layout

    def isTotal(self):
        return self._chk_total.isChecked()

    def isBackground(self):
        return self._chk_background.isChecked()

    def isErrorbar(self):
        return self._chk_errorbar.isChecked()

class PhotonSpectrumResultWidget(_FigureResultWidget):

    def _initToolbox(self):
        toolbox = _FigureResultWidget._initToolbox(self)

        itm_detector = DetectorToolItem(self)
        toolbox.addItem(itm_detector, "Detector")

        self._itm_options = _PhotonSpectrumResultOptionsToolItem(self)
        self._itm_options.stateChanged.connect(self._onOptionsChanged)
        toolbox.addItem(self._itm_options, "Options")

        return toolbox

    def _createFigure(self):
        fig = Figure()
        self._ax = fig.add_subplot("111")
        return fig

    def _drawFigure(self):
        colors = matplotlib.rcParams['axes.color_cycle']
        kwargs = {'linestyle': '-', 'marker': None}
        errorbar = self._itm_options.isErrorbar()

        if self._itm_options.isTotal():
            total = self.result().get_total()

            total_kwargs = kwargs.copy()
            total_kwargs.update(color=colors[0], label='Total')

            if errorbar:
                self._ax.errorbar(total[:, 0], total[:, 1], total[:, 2],
                                  ecolor=colors[0], **total_kwargs)
            else:
                self._ax.plot(total[:, 0], total[:, 1], **total_kwargs)

        if self._itm_options.isBackground():
            bckg = self.result().get_background()

            bckg_kwargs = kwargs.copy()
            bckg_kwargs.update(color=colors[1], label='Background')

            if errorbar:
                self._ax.errorbar(bckg[:, 0], bckg[:, 1], bckg[:, 2],
                                  ecolor=colors[1], **bckg_kwargs)
            else:
                self._ax.plot(bckg[:, 0], bckg[:, 1], **bckg_kwargs)

        self._ax.set_xlabel('Energy (eV)')
        self._ax.set_ylabel('Intensity (counts / (sr.eV.electron))')

        self._ax.legend(loc='best')

        _FigureResultWidget._drawFigure(self)

    def _onOptionsChanged(self):
        self._ax.clear()
        self._drawFigure()

    def dump(self):
        data = np.hstack((self.result().get_total(),
                          self.result().get_background()))
        return data

class _PhotonIntensityResultOptionsToolItem(_ResultToolItem):

    def _initUI(self):
        # Variables
        solidangle_sr = self.options().detectors[self.key()].solidangle_sr
        self._factors = {'counts / (s.A)': solidangle_sr / physics.e,
                         'counts / (s.nA)': solidangle_sr / physics.e / 1e9}

        # Widgets
        self._cb_unit = QComboBox()
        self._cb_unit.addItem('counts / (sr.electron)')
        self._cb_unit.addItem('counts / (s.A)')
        self._cb_unit.addItem('counts / (s.nA)')

        self._chk_uncertainty = QCheckBox('Show uncertainties')
        self._chk_uncertainty.setChecked(True)

        self._chk_pg = QCheckBox('No fluorescence')
        self._chk_pg.setChecked(True)

        self._chk_cg = QCheckBox('Characteristic fluorescence')
        self._chk_cg.setChecked(True)

        self._chk_bg = QCheckBox('Bremsstrahlung fluorescence')
        self._chk_bg.setChecked(True)

        self._chk_tg = QCheckBox('Total')
        self._chk_tg.setChecked(True)

        self._chk_pe = QCheckBox('No fluorescence')
        self._chk_pe.setChecked(True)

        self._chk_ce = QCheckBox('Characteristic fluorescence')
        self._chk_ce.setChecked(True)

        self._chk_be = QCheckBox('Bremsstrahlung fluorescence')
        self._chk_be.setChecked(True)

        self._chk_te = QCheckBox('Total')
        self._chk_te.setChecked(True)

        # Layouts
        layout = _ResultToolItem._initUI(self)
        layout.addRow("Unit", self._cb_unit)
        layout.addRow(self._chk_uncertainty)

        boxlayout = QVBoxLayout()
        boxlayout.addWidget(self._chk_pg)
        boxlayout.addWidget(self._chk_cg)
        boxlayout.addWidget(self._chk_bg)
        boxlayout.addWidget(self._chk_tg)

        box_generated = QGroupBox("Generated intensities (no absorption)")
        box_generated.setLayout(boxlayout)
        layout.addRow(box_generated)

        boxlayout = QVBoxLayout()
        boxlayout.addWidget(self._chk_pe)
        boxlayout.addWidget(self._chk_ce)
        boxlayout.addWidget(self._chk_be)
        boxlayout.addWidget(self._chk_te)

        box_emitted = QGroupBox('Emitted intensities (with absorption)')
        box_emitted.setLayout(boxlayout)
        layout.addRow(box_emitted)

        # Signals
        self._cb_unit.currentIndexChanged.connect(self.stateChanged)
        self._chk_uncertainty.stateChanged.connect(self.stateChanged)
        self._chk_pg.stateChanged.connect(self.stateChanged)
        self._chk_cg.stateChanged.connect(self.stateChanged)
        self._chk_bg.stateChanged.connect(self.stateChanged)
        self._chk_tg.stateChanged.connect(self.stateChanged)
        self._chk_pe.stateChanged.connect(self.stateChanged)
        self._chk_ce.stateChanged.connect(self.stateChanged)
        self._chk_be.stateChanged.connect(self.stateChanged)
        self._chk_te.stateChanged.connect(self.stateChanged)

        return layout

    def showUncertainty(self):
        return self._chk_uncertainty.isChecked()

    def showGenerated(self):
        return (self._chk_pg.isChecked(), self._chk_cg.isChecked(),
                self._chk_bg.isChecked(), self._chk_tg.isChecked())

    def showEmitted(self):
        return (self._chk_pe.isChecked(), self._chk_ce.isChecked(),
                self._chk_be.isChecked(), self._chk_te.isChecked())

    def factor(self):
        unit = self._cb_unit.currentText()
        return self._factors.get(unit, 1.0)

class _PhotonIntensityResultAbbreviationToolItem(_ResultToolItem):

    def _initUI(self):
        # Layouts
        layout = _ResultToolItem._initUI(self)
        layout.addRow("<b>P</b>", QLabel("primary photons (from electron interactions)"))
        layout.addRow("<b>C</b>", QLabel("fluorescence from characteristic x rays"))
        layout.addRow("<b>B</b>", QLabel("fluorescence from Bremsstrahlung x rays"))
        layout.addRow("<b>T</b>", QLabel("P+C+B, total intensity"))
        layout.addRow(QLabel(""))
        layout.addRow("<b>G</b>", QLabel("generated intensity (no absorption)"))
        layout.addRow("<b>E</b>", QLabel("emitted intensity (with absorption)"))

        return layout

class _PhotonIntensityResultTableModel(QAbstractTableModel):

    def __init__(self, result):
        QAbstractTableModel.__init__(self)
        self._result = result
        self._transitions = sorted(result.iter_transitions())

        self._header_sections = \
            ['Transition', 'PG', 'PE', 'CG', 'CE', 'BG', 'BE', 'TG', 'TE']
        self._data_funcs = \
            [lambda r, t: r.intensity(t, False, False),
             lambda r, t: r.intensity(t, True, False),
             lambda r, t: r.characteristic_fluorescence(t, False),
             lambda r, t: r.characteristic_fluorescence(t, True),
             lambda r, t: r.bremsstrahlung_fluorescence(t, False),
             lambda r, t: r.bremsstrahlung_fluorescence(t, True),
             lambda r, t: r.intensity(t, False, True),
             lambda r, t: r.intensity(t, True, True)]

        self._show_uncertainty = True
        self._factor = 1.0

    def rowCount(self, *args, **kwargs):
        return len(self._transitions)

    def columnCount(self, *args, **kwargs):
        return 9

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._transitions)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()

        transition = self._transitions[row]
        if column == 0:
            return str(transition)
        else:
            val, unc = self._data_funcs[column - 1](self._result, transition)
            val *= self._factor
            unc *= self._factor

            if self._show_uncertainty:
                return u'{0:n} \u00b1 {1:n}'.format(val, unc)
            else:
                return u'{0:n}'.format(val)

    def headerData(self, section , orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._header_sections[section]
        elif orientation == Qt.Vertical:
            return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))

    def setShowUncertainty(self, state):
        self._show_uncertainty = state
        self.reset()

    def setFactor(self, factor):
        self._factor = factor
        self.reset()

class PhotonIntensityResultWidget(_SaveableResultWidget):

    def _initUI(self):
        # Variables
        model = _PhotonIntensityResultTableModel(self.result())

        # Widgets
        self._table = QTableView()
        self._table.setModel(model)
        header = self._table.horizontalHeader()
        for i in range(1, 9):
            header.setResizeMode(i, QHeaderView.Stretch)

        # Layouts
        layout = _SaveableResultWidget._initUI(self)
        layout.addWidget(self._table)

        return layout

    def _initToolbox(self):
        toolbox = _SaveableResultWidget._initToolbox(self)

        self._itm_abbrev = _PhotonIntensityResultAbbreviationToolItem(self)
        toolbox.addItem(self._itm_abbrev, "Abbreviations")

        itm_detector = DetectorToolItem(self)
        toolbox.addItem(itm_detector, "Detector")

        self._itm_options = _PhotonIntensityResultOptionsToolItem(self)
        self._itm_options.stateChanged.connect(self._onOptionsChanged)
        toolbox.addItem(self._itm_options, "Options")

        return toolbox

    def _onOptionsChanged(self):
        model = self._table.model()
        model.setShowUncertainty(self._itm_options.showUncertainty())

        pg, cg, bg, tg = self._itm_options.showGenerated()
        pe, ce, be, te = self._itm_options.showEmitted()
        self._table.setColumnHidden(1, not pg)
        self._table.setColumnHidden(2, not pe)
        self._table.setColumnHidden(3, not cg)
        self._table.setColumnHidden(4, not ce)
        self._table.setColumnHidden(5, not bg)
        self._table.setColumnHidden(6, not be)
        self._table.setColumnHidden(7, not tg)
        self._table.setColumnHidden(8, not te)

        factor = self._itm_options.factor()
        model.setFactor(factor)

    def dump(self):
        rows = []
        rows.append(['Transition',
                     'PG', 'PG unc', 'PE', 'PE unc',
                     'CG', 'CG unc', 'CE', 'CE unc',
                     'BG', 'BG unc', 'BE', 'BE unc',
                     'TG', 'TG unc', 'TE', 'TE unc'])

        result = self.result()
        for transition in result:
            row = [transition]
            row.extend(result.intensity(transition, False, False))
            row.extend(result.intensity(transition, True, False))
            row.extend(result.characteristic_fluorescence(transition, False))
            row.extend(result.characteristic_fluorescence(transition, True))
            row.extend(result.bremsstrahlung_fluorescence(transition, False))
            row.extend(result.bremsstrahlung_fluorescence(transition, True))
            row.extend(result.intensity(transition, False, True))
            row.extend(result.intensity(transition, True, True))
            rows.append(row)

        return rows

class TimeResultWidget(_SaveableResultWidget):

    def _initUI(self):
        # Widgets
        self._txt_time = QLineEdit()
        self._txt_time.setText(human_time(self.result().simulation_time_s))
        self._txt_time.setReadOnly(True)

        self._txt_speed = QLineEdit()
        self._txt_speed.setText(human_time(self.result().simulation_speed_s[0]))
        self._txt_speed.setReadOnly(True)

        # Layouts
        layout = _SaveableResultWidget._initUI(self)

        sublayout = QFormLayout()
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        sublayout.addRow('Total time of the simulation', self._txt_time)
        sublayout.addRow('Average time of one trajectory', self._txt_speed)
        layout.addLayout(sublayout)

        layout.addStretch()

        return layout

    def dump(self):
        result = self.result()
        return [['Simulation time (s)', 'Simulation speed (s)'],
                [result.simulation_time_s, result.simulation_speed_s[0]]]

class ElectronFractionResultWidget(_SaveableResultWidget):

    def _initUI(self):
        # Widgets
        val, unc = self.result().absorbed
        self._txt_absorbed = QLineEdit()
        self._txt_absorbed.setText(u'{0:n} \u00b1 {1:n}'.format(val, unc))
        self._txt_absorbed.setReadOnly(True)

        val, unc = self.result().backscattered
        self._txt_backscattered = QLineEdit()
        self._txt_backscattered.setText(u'{0:n} \u00b1 {1:n}'.format(val, unc))
        self._txt_backscattered.setReadOnly(True)

        val, unc = self.result().transmitted
        self._txt_transmitted = QLineEdit()
        self._txt_transmitted.setText(u'{0:n} \u00b1 {1:n}'.format(val, unc))
        self._txt_transmitted.setReadOnly(True)

        # Layouts
        layout = _SaveableResultWidget._initUI(self)

        sublayout = QFormLayout()
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        sublayout.addRow('Absorbed fraction', self._txt_absorbed)
        sublayout.addRow('Backscattered fraction', self._txt_backscattered)
        sublayout.addRow('Transmitted fraction', self._txt_transmitted)
        layout.addLayout(sublayout)

        layout.addStretch()

        return layout

    def dump(self):
        result = self.result()
        return [['', 'Absorbed', 'Backscattered', 'Transmitted'],
                ['Average', result.absorbed[0], result.backscattered[0], result.transmitted[0]],
                ['Std. Dev.', result.absorbed[1], result.backscattered[1], result.transmitted[1]]]

class ShowersStatisticsResultWidget(_SaveableResultWidget):

    def _initUI(self):
        # Widgets
        self._txt_showers = QLineEdit()
        self._txt_showers.setText(str(self.result().showers))

        # Layouts
        layout = _SaveableResultWidget._initUI(self)

        sublayout = QFormLayout()
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        sublayout.addRow('Number of showers', self._txt_showers)
        layout.addLayout(sublayout)

        layout.addStretch()

        return layout

    def dump(self):
        result = self.result()
        return [['Number of showers'],
                [result.showers]]

class _TransitionListModel(QAbstractListModel):

    def __init__(self, transitions=None):
        QAbstractListModel.__init__(self)
        self._transitions = transitions or []

    def rowCount(self, *args, **kwargs):
        return len(self._transitions)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._transitions)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        return str(self._transitions[index.row()])

    def transition(self, index):
        return self._transitions[index]

class _PhotonDistributionResultOptionsToolItem(_ResultToolItem):

    def _initUI(self):
        # Variables
        result = self.result()
        transitions = sorted(result.iter_transitions())
        transition0 = transitions[0]
        model = _TransitionListModel(transitions)

        # Widgets
        self._chk_errorbar = QCheckBox("Show error bars")
        self._chk_errorbar.setChecked(True)

        self._cb_transition = QComboBox()
        self._cb_transition.setModel(model)
        self._cb_transition.setCurrentIndex(0)

        self._chk_pg = QCheckBox('No absorption, no fluorescence')
        state = result.exists(transition0, True, False, False, False)
        self._chk_pg.setEnabled(state)
        self._chk_pg.setChecked(state)

        self._chk_eg = QCheckBox('With absorption, no fluorescence')
        state = result.exists(transition0, True, True, False, False)
        self._chk_eg.setEnabled(state)
        self._chk_eg.setChecked(state)

        self._chk_pt = QCheckBox('No absorption, with fluorescence')
        state = result.exists(transition0, True, False, True, True)
        self._chk_pt.setEnabled(state)
        self._chk_pt.setChecked(state)

        self._chk_et = QCheckBox('With absorption, with fluorescence')
        state = result.exists(transition0, True, True, True, True)
        self._chk_et.setEnabled(state)
        self._chk_et.setChecked(state)

        # Layouts
        layout = _ResultToolItem._initUI(self)
        layout.addRow(self._chk_errorbar)
        layout.addRow('Transition', self._cb_transition)

        boxlayout = QVBoxLayout()
        boxlayout.addWidget(self._chk_pg)
        boxlayout.addWidget(self._chk_eg)
        boxlayout.addWidget(self._chk_pt)
        boxlayout.addWidget(self._chk_et)

        box_generated = QGroupBox("Curves")
        box_generated.setLayout(boxlayout)
        layout.addRow(box_generated)

        # Signals
        self._cb_transition.currentIndexChanged.connect(self._onTransitionChanged)
        self._chk_pg.stateChanged.connect(self.stateChanged)
        self._chk_eg.stateChanged.connect(self.stateChanged)
        self._chk_pt.stateChanged.connect(self.stateChanged)
        self._chk_et.stateChanged.connect(self.stateChanged)
        self._chk_errorbar.stateChanged.connect(self.stateChanged)

        return layout

    def _onTransitionChanged(self):
        result = self.result()

        index = self._cb_transition.currentIndex()
        transition = self._cb_transition.model().transition(index)

        self._chk_pg.setEnabled(result.exists(transition, True, False, False, False))
        self._chk_eg.setEnabled(result.exists(transition, True, True, False, False))
        self._chk_pt.setEnabled(result.exists(transition, True, False, True, True))
        self._chk_et.setEnabled(result.exists(transition, True, True, True, True))

        self.stateChanged.emit()

    def transition(self):
        index = self._cb_transition.currentIndex()
        return self._cb_transition.model().transition(index)

    def showConditions(self):
        return (self._chk_pg.isChecked() and self._chk_pg.isEnabled(),
                self._chk_eg.isChecked() and self._chk_eg.isEnabled(),
                self._chk_pt.isChecked() and self._chk_pt.isEnabled(),
                self._chk_et.isChecked() and self._chk_et.isEnabled())

    def showErrorbar(self):
        return self._chk_errorbar.isChecked()

class _PhotonDistributionResultWidget(_FigureResultWidget):

    def _initToolbox(self):
        toolbox = _FigureResultWidget._initToolbox(self)

        itm_detector = DetectorToolItem(self)
        toolbox.addItem(itm_detector, "Detector")

        self._itm_options = _PhotonDistributionResultOptionsToolItem(self)
        self._itm_options.stateChanged.connect(self._onOptionsChanged)
        toolbox.addItem(self._itm_options, 'Options')

        return toolbox

    def _createFigure(self):
        fig = Figure()
        self._ax = fig.add_subplot("111")
        return fig

    def _drawFigure(self):
        result = self.result()

        def _plot(transition, absorption, fluorescence, label, color_index):
            if not result.exists(transition, True, absorption,
                                 fluorescence, fluorescence):
                return
            dist = result.get(transition, absorption, fluorescence)

#            self._ax.plot(dist[:, 0], dist[:, 1])

            dist_kwargs = kwargs.copy()
            dist_kwargs.update(color=colors[color_index], label=label)

            if errorbar:
                self._ax.errorbar(dist[:, 0], dist[:, 1], dist[:, 2],
                                  ecolor=colors[color_index], **dist_kwargs)
            else:
                self._ax.plot(dist[:, 0], dist[:, 1], **dist_kwargs)

        transition = self._itm_options.transition()
        pg, eg, pt, et = self._itm_options.showConditions()

        colors = matplotlib.rcParams['axes.color_cycle']
        kwargs = {'linestyle': '-', 'marker': None}
        errorbar = self._itm_options.showErrorbar()

        if pg:
            _plot(transition, False, False, 'No absorption, no fluorescence', 0)
        if eg:
            _plot(transition, True, False, 'With absorption, no fluorescence', 1)
        if pt:
            _plot(transition, False, True, 'No absorption, with fluorescence', 2)
        if et:
            _plot(transition, True, True, 'With absorption, with fluorescence', 3)

        self._ax.set_ylabel('Intensity (counts / (sr.eV.electron))')

        self._ax.legend(loc='best')

        _FigureResultWidget._drawFigure(self)

    def _onOptionsChanged(self):
        self._ax.clear()
        self._drawFigure()

    def dump(self):
        result = self.result()
        transition = self._itm_options.transition()

        arr = np.zeros((0, 3))

        pg, eg, pt, et = self._itm_options.showConditions()

        if pg and result.exists(transition, True, False, False, False):
            arr = np.vstack((arr, result.get(transition, False, False)))
        if eg and result.exists(transition, True, True, False, False):
            arr = np.vstack((arr, result.get(transition, True, False)))
        if pt and result.exists(transition, True, False, True, True):
            arr = np.vstack((arr, result.get(transition, False, True)))
        if et and result.exists(transition, True, True, True):
            arr = np.vstack((arr, result.get(transition, True, True)))

        return arr

class PhotonDepthResultWidget(_PhotonDistributionResultWidget):

    def _drawFigure(self):
        self._ax.set_xlabel('Depth (m)')
        _PhotonDistributionResultWidget._drawFigure(self)

class PhiZResultWidget(_PhotonDistributionResultWidget):

    def _drawFigure(self):
        self._ax.set_xlabel('Depth (m)')
        _PhotonDistributionResultWidget._drawFigure(self)

class PhotonRadialResultWidget(_PhotonDistributionResultWidget):

    def _drawFigure(self):
        self._ax.set_xlabel('Radius (m)')
        _PhotonDistributionResultWidget._drawFigure(self)

class _ChannelsResultOptionsToolItem(_ResultToolItem):

    def _initUI(self):
        # Widgets
        self._chk_errorbar = QCheckBox("Show error bars")
        self._chk_errorbar.setChecked(True)

        # Layouts
        layout = _ResultToolItem._initUI(self)
        layout.addRow(self._chk_errorbar)

        # Signals
        self._chk_errorbar.stateChanged.connect(self.stateChanged)

        return layout

    def showErrorbar(self):
        return self._chk_errorbar.isChecked()

class _ChannelsResultWidget(_FigureResultWidget):

    def _initToolbox(self):
        toolbox = _FigureResultWidget._initToolbox(self)

        itm_detector = DetectorToolItem(self)
        toolbox.addItem(itm_detector, "Detector")

        self._itm_options = _ChannelsResultOptionsToolItem(self)
        self._itm_options.stateChanged.connect(self._onOptionsChanged)
        toolbox.addItem(self._itm_options, 'Options')

        return toolbox

    def _createFigure(self):
        fig = Figure()
        self._ax = fig.add_subplot("111")
        return fig

    def _drawFigure(self):
        data = self._getData()

        colors = matplotlib.rcParams['axes.color_cycle']
        kwargs = {'linestyle': '-', 'marker': None, 'color': colors[0]}
        errorbar = self._itm_options.showErrorbar()

        if errorbar:
            self._ax.errorbar(data[:, 0], data[:, 1], data[:, 2],
                              ecolor=colors[0], **kwargs)
        else:
            self._ax.plot(data[:, 0], data[:, 1], **kwargs)

        _FigureResultWidget._drawFigure(self)

    def _getData(self):
        return self.result().get_data()

    def _onOptionsChanged(self):
        self._ax.clear()
        self._drawFigure()

    def dump(self):
        return self._getData()

class _EnergyResultWidget(_ChannelsResultWidget):

    def _drawFigure(self):
        self._ax.set_xlabel('Energy (eV)')
        self._ax.set_ylabel('Probability density (counts/(eV.electron))')
        _ChannelsResultWidget._drawFigure(self)

class BackscatteredElectronEnergyResultWidget(_ChannelsResultWidget):
    pass

class TransmittedElectronEnergyResultWidget(_ChannelsResultWidget):
    pass

class _AngleResultWidget(_ChannelsResultWidget):

    def _getData(self):
        data = _ChannelsResultWidget._getData(self)
        data[:, 0] = np.degrees(data[:, 0])
        return data

    def _drawFigure(self):
        self._ax.set_xlabel('Angle (\u00b0)')
        self._ax.set_ylabel('Probability density (counts/sr)')
        _ChannelsResultWidget._drawFigure(self)

class BackscatteredElectronAzimuthalAngularResultWidget(_ChannelsResultWidget):
    pass

class TransmittedElectronAzimuthalAngularResultWidget(_ChannelsResultWidget):
    pass

class BackscatteredElectronPolarAngularResultWidget(_ChannelsResultWidget):
    pass

class TransmittedElectronPolarAngularResultWidget(_ChannelsResultWidget):
    pass

class BackscatteredElectronRadialResultWidget(_ChannelsResultWidget):

    def _drawFigure(self):
        self._ax.set_xlabel('Radius (m)')
        self._ax.set_ylabel('Probability density (counts/(eV.electron.m2))')
        _ChannelsResultWidget._drawFigure(self)

#--- Functions

def get_widget_class(clasz):
    return _get_widget_class('pymontecarlo.ui.gui.results.result', clasz)




#!/usr/bin/env python
"""
================================================================================
:mod:`summary` -- Summary dialog
================================================================================

.. module:: summary
   :synopsis: Summary dialog

.. inheritance-diagram:: pymontecarlo.ui.gui.results.summary

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
import numbers
from operator import methodcaller
from collections import OrderedDict

# Third party modules.
from PySide.QtGui import \
    (QComboBox, QListView, QDialog, QFormLayout, QDialogButtonBox, QAction,
     QToolBar, QWidget, QSizePolicy, QLineEdit, QMessageBox, QCheckBox)
from PySide.QtCore import Qt, QAbstractListModel

import numpy as np

import matplotlib
from matplotlib.figure import Figure

import latexcodec #@UnusedImport

# Local modules.
from pymontecarlo.util.parameter import iter_getters

from pymontecarlo.results.result import _SummarizableResult

from pymontecarlo.ui.gui.results.results import _FigureResultMixin, _BaseResultWidget, _BaseResultToolItem
from pymontecarlo.ui.gui.util.tango import getIcon

# Globals and constants variables.

class _ResultsToolItem(_BaseResultToolItem):

    def __init__(self, parent):
        self._results = parent.results()
        _BaseResultToolItem.__init__(self, parent)

    def results(self):
        return self._results

class _Series(object):

    def __init__(self, name, conditions, summary_key):
        self.name = name
        self.conditions = conditions
        self.summary_key = summary_key

    def match(self, options):
        for _name, getter, expected in self.conditions:
            actual = getter(options)
            if expected != actual:
                return False
        return True

class _ValuesModel(QAbstractListModel):

        def __init__(self, values):
            QAbstractListModel.__init__(self)
            try:
                values = sorted(values)
            except TypeError:
                pass
            self._values = list(values)

        def rowCount(self, *args, **kwargs):
            return len(self._values)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < self.rowCount()):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            return str(self._values[index.row()])

        def value(self, index):
            return self._values[index]

        def valueIndex(self, value):
            return self._values.index(value)

class _SeriesDialog(QDialog):

    def __init__(self, results, result_key,
                 parameter_getters, x_parameter_name,
                 series=None, parent=None):
        QDialog.__init__(self, parent)

        # Variables
        self._results = results
        self._result_key = result_key
        self._parameter_getters = parameter_getters
        options = results.options

        # Widgets
        self._txt_name = QLineEdit()

        self._cb_parameters = {}
        for name, getter in parameter_getters.items():
            if name == x_parameter_name:
                continue

            combobox = QComboBox()
            values = np.array(getter(options), ndmin=1)
            combobox.setModel(_ValuesModel(values))
            self._cb_parameters[name] = combobox

        self._cb_summary_key = QComboBox()
        self._cb_summary_key.setModel(_ValuesModel([]))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layouts
        layout = QFormLayout()
        if sys.platform == 'darwin': # Fix for Mac OS
            layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layout.addRow('Name', self._txt_name)
        for name, combobox in self._cb_parameters.items():
            layout.addRow(name, combobox)
        layout.addRow('Summary variable', self._cb_summary_key)

        layout.addRow(buttons)

        self.setLayout(layout)

        # Signals
        buttons.accepted.connect(self._onOk)
        buttons.rejected.connect(self.reject)

        for combobox in self._cb_parameters.values():
            combobox.currentIndexChanged.connect(self._onParameterChanged)

        # Defaults
        if series is not None:
            self._txt_name.setText(series.name)

            for name, _, value in series.conditions:
                combobox = self._cb_parameters[name]
                index = combobox.model().valueIndex(value)
                combobox.setCurrentIndex(index)
            self._onParameterChanged()

            index = self._cb_summary_key.model().valueIndex(series.summary_key)
            self._cb_summary_key.setCurrentIndex(index)
        else:
            self._onParameterChanged()

    def _onParameterChanged(self):
        summary_keys = set()

        for container in self._results:
            match = True
            for name, expected in self.parameterValue().items():
                getter = self._parameter_getters[name]
                actual = getter(container.options)
                if actual != expected:
                    match = False
                    break

            if not match:
                continue

            try:
                result = container[self._result_key]
            except KeyError:
                continue

            summary_keys.update(result.get_summary().keys())

        self._cb_summary_key.setModel(_ValuesModel(summary_keys))

    def _onOk(self):
        if self._cb_summary_key.currentIndex() < 0:
            return
        self.accept()

    def name(self):
        name = self._txt_name.text().strip()

        if not name:
            parts = []
            for param_name, value in self.parameterValue().items():
                parts.append('%s=%s' % (param_name, value))
            parts.append('summary=%s' % self.summaryKey())
            name = '+'.join(parts)

        return name

    def parameterValue(self):
        parameter_value = {}
        for name, combobox in self._cb_parameters.items():
            try:
                value = combobox.model().value(combobox.currentIndex())
                parameter_value[name] = value
            except IndexError:
                continue
        return parameter_value

    def summaryKey(self):
        return self._cb_summary_key.model().value(self._cb_summary_key.currentIndex())

class _SeriesModel(QAbstractListModel):

        def __init__(self):
            QAbstractListModel.__init__(self)
            self._list_series = []

        def rowCount(self, *args, **kwargs):
            return len(self._list_series)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < self.rowCount()):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            return str(self._list_series[index.row()].name)

        def addSeries(self, series):
            self._list_series.append(series)
            self.reset()

        def removeSeries(self, index):
            self._list_series.pop(index)
            self.reset()

        def clearSeries(self):
            self._list_series.clear()
            self.reset()

        def updateSeries(self, index, series):
            self._list_series[index] = series
            self.reset()

        def series(self, index):
            return self._list_series[index]

        def listSeries(self):
            return self._list_series[:]

class _SummaryOptionsToolItem(_ResultsToolItem):

    def _initUI(self):
        # Variables
        self._parameter_getters = {}

        def _program_getter(options):
            programs = list(options.programs)
            if len(programs) == 1:
                return programs[0]
            else:
                return list(programs)
        self._parameter_getters['program'] = _program_getter

        options = self.options()
        for name, getter in iter_getters(options):
            values = np.array(getter(options), ndmin=1)
            if len(values) < 2:
                continue
            self._parameter_getters[name] = getter

        # Actions
        act_add_series = QAction(getIcon("list-add"), "Add series", self)
        act_remove_series = QAction(getIcon("list-remove"), "Remove series", self)
        act_clear_series = QAction(getIcon("edit-clear"), "Clear", self)

        # Widgets
        self._cb_result_key = QComboBox()

        self._cb_x_parameter = QComboBox()
        self._cb_x_parameter.addItems(list(self._parameter_getters.keys()))

        self._lst_series = QListView()
        self._lst_series.setModel(_SeriesModel())

        tlb_series = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tlb_series.addWidget(spacer)
        tlb_series.addAction(act_add_series)
        tlb_series.addAction(act_remove_series)
        tlb_series.addAction(act_clear_series)

        self._chk_normalize = QCheckBox('Normalize series')

        # Layouts
        layout = _ResultsToolItem._initUI(self)
        layout.addRow("Result", self._cb_result_key)
        layout.addRow("X parameter", self._cb_x_parameter)
        layout.addRow("Series", self._lst_series)
        layout.addRow(tlb_series)
        layout.addRow(self._chk_normalize)

        # Signals
        act_add_series.triggered.connect(self._onAddSeries)
        act_remove_series.triggered.connect(self._onRemoveSeries)
        act_clear_series.triggered.connect(self._onClearSeries)
        self._lst_series.doubleClicked.connect(self._onSeriesDoubleClicked)
        self._cb_result_key.currentIndexChanged.connect(self._onResultKeyChanged)
        self._chk_normalize.stateChanged.connect(self.stateChanged)

        # Defaults
        keys = set()
        for container in self.results():
            for key, result in container.items():
                if not isinstance(result, _SummarizableResult):
                    continue
                keys.add(key)
        self._cb_result_key.addItems(sorted(keys))

        return layout

    def _onResultKeyChanged(self):
        ndim = self._getResultDimensions()
        self._cb_x_parameter.setEnabled(ndim == 1)

    def _onAddSeries(self):
        # Dialog
        result_key = self._cb_result_key.currentText()

        if self._getResultDimensions() > 1:
            x_parameter_name = None
        else:
            x_parameter_name = self._cb_x_parameter.currentText()

        dialog = _SeriesDialog(self.results(), result_key,
                               self._parameter_getters, x_parameter_name)
        if not dialog.exec_():
            return

        # Create series
        series_name = dialog.name()
        parameter_value = dialog.parameterValue()
        summary_key = dialog.summaryKey()

        conditions = []
        for name, value in parameter_value.items():
            conditions.append((name, self._parameter_getters[name], value))

        model = self._lst_series.model()
        model.addSeries(_Series(series_name, conditions, summary_key))

        # Update widgets
        self._cb_result_key.setEnabled(False)
        self._cb_x_parameter.setEnabled(False)

        self.stateChanged.emit()

    def _onRemoveSeries(self):
        selection = self._lst_series.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Series", "Select a row")
            return

        model = self._lst_series.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            model.removeSeries(row)

        enabled = model.rowCount() == 0
        self._cb_result_key.setEnabled(enabled)
        self._cb_x_parameter.setEnabled(enabled)

        self.stateChanged.emit()

    def _onClearSeries(self):
        model = self._lst_series.model()
        model.clearSeries()

        self._cb_result_key.setEnabled(True)
        self._cb_x_parameter.setEnabled(True)

        self.stateChanged.emit()

    def _onSeriesDoubleClicked(self, index):
        series = self._lst_series.model().series(index.row())

        # Dialog
        result_key = self._cb_result_key.currentText()

        if self._getResultDimensions() > 1:
            x_parameter_name = None
        else:
            x_parameter_name = self._cb_x_parameter.currentText()

        dialog = _SeriesDialog(self.results(), result_key,
                               self._parameter_getters, x_parameter_name,
                               series)
        if not dialog.exec_():
            return

        # Create series
        series_name = dialog.name()
        parameter_value = dialog.parameterValue()
        summary_key = dialog.summaryKey()

        conditions = []
        for name, value in parameter_value.items():
            conditions.append((name, self._parameter_getters[name], value))

        model = self._lst_series.model()
        model.updateSeries(index.row(),
                           _Series(series_name, conditions, summary_key))

        self.stateChanged.emit()

    def _getResultDimensions(self):
        result_key = self._cb_result_key.currentText()

        for container in self.results():
            try:
                result = container[result_key]
            except KeyError:
                continue
            ndim = result.get_dimensions()

        return ndim

    def resultKey(self):
        return self._cb_result_key.currentText() or None

    def xParameterName(self):
        if self._getResultDimensions() > 1:
            return None
        return self._cb_x_parameter.currentText() or None

    def xParameterGetter(self):
        if self._getResultDimensions() > 1:
            return None
        text = self._cb_x_parameter.currentText()
        return self._parameter_getters.get(text)

    def listSeries(self):
        return self._lst_series.model().listSeries()

    def isNormalize(self):
        return self._chk_normalize.isChecked()

class SummaryWidget(_FigureResultMixin, _BaseResultWidget):

    def __init__(self, results, parent=None):
        self._results = results
        _FigureResultMixin.__init__(self)
        _BaseResultWidget.__init__(self, results.options, parent)
        self.setTitle("Summary")
        self._drawFigure()

    def _initToolbox(self):
        toolbox = super(SummaryWidget, self)._initToolbox()

        self._itm_options = _SummaryOptionsToolItem(self)
        self._itm_options.stateChanged.connect(self._onOptionsChanged)
        toolbox.addItem(self._itm_options, "Options")

        return toolbox

    def _generateData(self):
        result_key = self._itm_options.resultKey()
        x_parameter_getter = self._itm_options.xParameterGetter()
        list_series = self._itm_options.listSeries()

        if not result_key or not list_series:
            return {}

        logging.debug(list_series)

        data = OrderedDict()
        for container in self.results():
            try:
                result = container[result_key]
            except KeyError:
                continue

            options = container.options
            summary = result.get_summary()

            for series in list_series:
                if not series.match(options):
                    continue

                try:
                    datum = summary[series.summary_key]
                except KeyError:
                    continue

                data.setdefault(series.name, {})

                if x_parameter_getter is not None:
                    x = x_parameter_getter(options)
                    data[series.name].setdefault('xs', []).append(x)

                    y = datum[0][0]
                    data[series.name].setdefault('ys', []).append(y)
                else:
                    xs = datum[:, 0]
                    data[series.name]['xs'] = xs

                    ys = datum[:, 1]
                    data[series.name]['ys'] = ys

        return data

    def _createFigure(self):
        fig = Figure()
        self._ax = fig.add_subplot("111")
        return fig

    def _drawFigure(self):
        # Data
        data = self._generateData()
        logging.debug(data)

        if not data:
            _FigureResultMixin._drawFigure(self)
            return

        # Labels
        result_key = self._itm_options.resultKey()
        x_parameter_name = self._itm_options.xParameterName()

        xlabel = None
        ylabel = None
        for container in self.results():
            try:
                result = container[result_key]
            except KeyError:
                continue

            labels = result.get_labels()

            if x_parameter_name is not None:
                xlabel = x_parameter_name
                ylabel = labels[0]
            else:
                xlabel = labels[0]
                ylabel = labels[1]

        # Plot
        colors = matplotlib.rcParams['axes.color_cycle']
        kwargs = {'linestyle': '-', 'marker': None}
        is_normalize = self._itm_options.isNormalize()

        for i, name in enumerate(data.keys()):
            try:
                datum = data[name]
            except KeyError:
                continue

            xs = datum['xs']
            ys = datum['ys']

            if not all(map(lambda x: isinstance(x, numbers.Number), xs)):
                ticklabels = list(map(str, xs))
                xs = range(len(xs))
            else:
                ticklabels = None

            if is_normalize:
                ys = (ys - np.min(ys)) / np.ptp(ys)

            self._ax.plot(xs, ys, label=name.encode('latex').decode('ascii'),
                          color=colors[i % len(colors)], **kwargs)

            if ticklabels:
                self._ax.set_xticks(xs)
                self._ax.set_xticklabels(ticklabels)

        self._ax.legend(loc='best')
        self._ax.set_xlabel(xlabel)
        self._ax.set_ylabel(ylabel)

        _FigureResultMixin._drawFigure(self)

    def dump(self):
        data = self._generateData()

        rows = []
        for name, datum in data.items():
            rows.append([name])
            rows.extend(zip(datum['xs'], datum['ys']))

        return rows

    def _onOptionsChanged(self):
        self._ax.clear()
        self._drawFigure()

    def results(self):
        return self._results

def __run():
    from PySide.QtGui import QMainWindow, QApplication
    from pymontecarlo.options.options import Options
    from pymontecarlo.results.results import Results
    from pymontecarlo.options.detector import \
        PhotonIntensityDetector, PhotonDepthDetector
    from pymontecarlo.results.result import \
        PhotonKey, PhotonIntensityResult, PhotonDepthResult
    from pyxray.transition import K_family

    # Results
    ops = Options(name='base')
    ops.beam.energy_keV = [5.0, 10.0]
    ops.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
    ops.detectors['det2'] = PhotonDepthDetector((0, 1), (0, 1), 4)

    ops1 = Options(name='test1')
    ops1.beam.energy_keV = 5.0
    ops1.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
    ops1.detectors['det2'] = PhotonDepthDetector((0, 1), (0, 1), 4)
    intensities = {}
    intensities[PhotonKey(K_family(13), True, PhotonKey.T)] = (1.0, 0.1)
    intensities[PhotonKey(K_family(14), True, PhotonKey.T)] = (10.0, 0.1)
    result11 = PhotonIntensityResult(intensities)
    distributions = {}
    et = np.array([[1.0, 2.0, 3.0, 4.0],
                   [30.0, 35.0, 34.0, 31.0],
                   [0.31, 0.32, 0.33, 0.34]]).T
    distributions[PhotonKey(K_family(13), True, PhotonKey.T)] = et
    et = np.array([[1.0, 2.0, 3.0, 4.0],
                   [31.0, 36.0, 35.0, 32.0],
                   [0.31, 0.32, 0.33, 0.34]]).T
    distributions[PhotonKey(K_family(14), True, PhotonKey.T)] = et
    result12 = PhotonDepthResult(distributions)

    ops2 = Options(name='test2')
    ops2.beam.energy_keV = 10.0
    ops2.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
    ops2.detectors['det2'] = PhotonDepthDetector((0, 1), (0, 1), 4)
    intensities = {}
    intensities[PhotonKey(K_family(13), True, PhotonKey.T)] = (2.0, 0.2)
    intensities[PhotonKey(K_family(14), True, PhotonKey.T)] = (3.0, 0.1)
    result21 = PhotonIntensityResult(intensities)
    distributions = {}
    et = np.array([[1.0, 2.0, 3.0, 4.0],
                   [10.0, 15.0, 14.0, 11.0],
                   [0.11, 0.12, 0.13, 0.14]]).T
    distributions[PhotonKey(K_family(13), True, PhotonKey.T)] = et
    et = np.array([[1.0, 2.0, 3.0, 4.0],
                   [11.0, 16.0, 15.0, 12.0],
                   [0.11, 0.12, 0.13, 0.14]]).T
    distributions[PhotonKey(K_family(14), True, PhotonKey.T)] = et
    result22 = PhotonDepthResult(distributions)

    list_results = [(ops1, {'det1': result11, 'det2': result12}),
                    (ops2, {'det1': result21, 'det2': result22})]
    results = Results(ops, list_results)

    app = QApplication(sys.argv)
    window = QMainWindow()

    widget = SummaryWidget(results)


    window.setCentralWidget(widget)

    window.show()

    app.exec_()

if __name__ == '__main__':
    __run()

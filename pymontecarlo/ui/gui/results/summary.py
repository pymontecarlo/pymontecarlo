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
import numbers

# Third party modules.
from PySide.QtGui import QComboBox, QListWidget

import numpy as np

import matplotlib
from matplotlib.figure import Figure

# Local modules.
from pymontecarlo.util.parameter import iter_getters

from pymontecarlo.results.result import _SummarizableResult

from pymontecarlo.ui.gui.results.results import _FigureResultMixin, _BaseResultWidget, _BaseResultToolItem

# Globals and constants variables.

class _ResultsToolItem(_BaseResultToolItem):

    def __init__(self, parent):
        self._results = parent.results()
        _BaseResultToolItem.__init__(self, parent)

    def results(self):
        return self._results

class _SummaryOptionsToolItem(_ResultsToolItem):

    def _initUI(self):
        # Variables
        self._parameter_getters = {'program': lambda ops: next(iter(ops.programs))}

        # Widgets
        self._cb_key = QComboBox()

        self._cb_parameter = QComboBox()

        self._lst_variable = QListWidget()
        self._lst_variable.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        # Layouts
        layout = _ResultsToolItem._initUI(self)
        layout.addRow("Result", self._cb_key)
        layout.addRow("Parameter", self._cb_parameter)
        layout.addRow("Variable(s)", self._lst_variable)

        # Signals
        self._cb_key.currentIndexChanged.connect(self.stateChanged)
        self._cb_key.currentIndexChanged.connect(self._onKeyChanged)
        self._cb_parameter.currentIndexChanged.connect(self.stateChanged)
        self._lst_variable.itemSelectionChanged.connect(self.stateChanged)

        # Defaults
        keys = set()
        for container in self.results():
            for key, result in container.items():
                if not isinstance(result, _SummarizableResult):
                    continue
                keys.add(key)
        self._cb_key.addItems(sorted(keys))

        options = self.options()
        self._cb_parameter.addItem('program')
        for name, getter in iter_getters(options):
            values = np.array(getter(options), ndmin=1)
            if len(values) < 2:
                continue
            self._parameter_getters[name] = getter
            self._cb_parameter.addItem(name)

        return layout

    def _onKeyChanged(self):
        self._lst_variable.clear()

        key = self._cb_key.currentText()
        variables = set()
        for container in self.results():
            result = container[key]
            variables.update(result.get_summary().keys())

        self._lst_variable.addItems(sorted(variables))

    def resultKey(self):
        return self._cb_key.currentText() or None

    def parameterName(self):
        return self._cb_parameter.currentText() or None

    def parameterGetter(self):
        text = self._cb_parameter.currentText()
        return self._parameter_getters.get(text)

    def variables(self):
        return [item.text() for item in self._lst_variable.selectedItems()]

class SummaryWidget(_FigureResultMixin, _BaseResultWidget):

    def __init__(self, results, parent=None):
        self._results = results
        _FigureResultMixin.__init__(self)
        _BaseResultWidget.__init__(self, results.options, parent)
        self.setTitle("Summary")
        self._drawFigure()

    def _initToolbox(self):
        toolbox = super(SummaryWidget, self)._initToolbox()

        self._itm_parameter = _SummaryOptionsToolItem(self)
        self._itm_parameter.stateChanged.connect(self._onOptionsChanged)
        toolbox.addItem(self._itm_parameter, "Options")

        return toolbox

    def _createFigure(self):
        fig = Figure()
        self._ax = fig.add_subplot("111")
        return fig

    def _drawFigure(self):
        result_key = self._itm_parameter.resultKey()
        parameter_name = self._itm_parameter.parameterName()
        parameter_getter = self._itm_parameter.parameterGetter()
        variables = self._itm_parameter.variables()
        if not result_key or not parameter_name or not variables:
            _FigureResultMixin._drawFigure(self)
            return

        colors = matplotlib.rcParams['axes.color_cycle']
        kwargs = {'linestyle': '-', 'marker': None}
        errorbar = True #self._itm_options.isErrorbar()

        data = {}
        y = None
        for container in self.results():
            result = container[result_key]
            summary = result.get_summary()
            labels = result.get_labels()
            x = parameter_getter(container.options)
            for variable in variables:
                try:
                    y = summary[variable]
                    data.setdefault(variable, {})[x] = y
                except KeyError:
                    continue

        if y is None:
            _FigureResultMixin._drawFigure(self)
            return

        def _draw(xs, ys, yes=None, **kwargs):
            if not all(map(lambda x: isinstance(x, numbers.Number), xs)):
                labels = xs
                xs = range(len(xs))
            else:
                labels = None

            if errorbar:
                self._ax.errorbar(xs, ys, yes, ecolor=kwargs['color'], **kwargs)
            else:
                self._ax.plot(xs, ys, **kwargs)

            if labels:
                self._ax.set_xticklabels(labels)

        if len(y) == 1:
            for i, variable in enumerate(sorted(data.keys())):
                xs = list(data[variable].keys())
                try:
                    xs = sorted(xs)
                except TypeError:
                    pass

                ys = []; yes = []
                for x in xs:
                    datum = data[variable][x]
                    ys.append(datum[0][0])
                    yes.append(datum[0][1])

                color = colors[i % len(colors)]
                kwargs.update(color=color, label=variable)

                _draw(xs, ys, yes, **kwargs)

            self._ax.set_xlabel(parameter_name)
            if len(data) == 1:
                self._ax.set_ylabel('%s - %s' % (next(iter(data.keys())), labels[0]))
            else:
                self._ax.legend(loc='best')
                self._ax.set_ylabel(labels[0])
        else:
            i = 0
            for variable in sorted(data.keys()):
                for x in data[variable]:
                    datum = data[variable][x]

                    color = colors[i % len(colors)]
                    if len(data) == 1:
                        label = str(x)
                    else:
                        label = '%s - %s' % (variable, x)
                    kwargs.update(color=color, label=label)

                    _draw(datum[:, 0], datum[:, 1], datum[:, 2], **kwargs)

                    i += 1

            self._ax.legend(loc='best')
            self._ax.set_xlabel(labels[0])
            self._ax.set_ylabel(labels[1])

        _FigureResultMixin._drawFigure(self)

    def _onOptionsChanged(self):
        self._ax.clear()
        self._drawFigure()

    def results(self):
        return self._results

def __run():
    import sys
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

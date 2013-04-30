#!/usr/bin/env python
"""
================================================================================
:mod:`experimentrunner` -- Runners to run experiments.
================================================================================

.. module:: experiment
   :synopsis: Runners to run experiments

.. inheritance-diagram:: pymontecarlo.runner.experiment
"""
# Script information for the file.
__author__ = "Niklas Mevenkamp"
__email__ = "niklas.mevenkamp@gmx.net"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Niklas Mevenkamp"
__license__ = "GPL v3"

# Standard library modules
import logging
import copy
import glob
import os

# Third party modules
from scipy.interpolate import SmoothBivariateSpline

# Local modules
from pymontecarlo.runner.base import _Runner
from pymontecarlo.reconstruction.experiment import Experiment


class ExperimentRunner(_Runner):
    def __init__(self, runner):
        """
        Creates a new experiment runner that can simulate experiments
        using the specified runner for the options files.
        
        :arg runner: instance of a runner class that can run options objects
        """

        _Runner.__init__(self, None)
        self._runner = runner
        self._lookup = {}

    def put(self, experiment):
        # TODO: check if experiment has already been put (or get rid of this), below code snippet does not work
        #if experiment.name in [exp.name for exp in self._list_experiments]:
        #    raise ValueError, "An experiment with the same name is already in the queue"

        # Put options of the measurements
        for measurement in experiment.get_measurements():
            if not measurement.simulated_unk():
                options = measurement.get_options_unk()
                options_uuid = self._runner.put(options)
                self._lookup[options_uuid] = {'type': 'unk', 'measurement': measurement}
                print options_uuid
            if measurement.has_standards() and not measurement.simulated_std():
                for transition in measurement.get_transitions():
                    options = copy.deepcopy(measurement.get_options_std(transition))
                    self._lookup[options.uuid] = \
                        {'type': 'std', 'measurement': measurement, 'transition': transition}

    def start(self):
        self._runner.start()

    def stop(self):
        self._runner.stop()

    def close(self):
        self._runner.close()

    def is_alive(self):
        return self._runner.is_alive()

    def join(self):
        self._runner.join()

    def get_results(self):
        list_experiments = []
        list_experiment_names = []
        list_results = self._runner.get_results()

        for results in list_results:
            print results.options.uuid
            lookup = self._lookup[results.options.uuid]
            if lookup['type'] == 'unk':
                lookup['measurement'].put_results(results)
            if lookup['type'] == 'std':
                lookup['measurement'].put_results_std(lookup['transition'], results)

            # Put experiment to output list (if not already there) and delete lookup
            if not lookup['experiment'].name in list_experiment_names:
                list_experiment_names.append(lookup['experiment'].name)
                list_experiments.append(lookup['experiment'])
            del self._lookup[results.options.uuid]

        return list_experiments

    def report(self):
        return self._runner.report()

class ExperimentInterp2DRunner(_Runner):
    def __init__(self, list_experiments_data):
        """
        Creates a new interpolation runner that can interpolate kratios that were
        measured in experiments with different values of the same parameters.
        Note: Interpolation is only available for experiments with 2 parameters.
        
        :arg list_experiments_data: a list of experiment objects used as data for interpolation
        """

        _Runner.__init__(self, None)
        self._list_experiments = []
        self._list_experiments_data = list_experiments_data

        self._data = self._collect_data(self._list_experiments_data)
        self._spline = self._get_spline(self._data)

    @classmethod
    def load(cls, dir_path):
        """
        Creates a new interpolation runner that can interpolate k-ratios that were
        measured in experiments with different values of the same parameters.
        Note: Interpolation is only available for experiments with 2 parameters.
        
        :arg dir_path: path pointing to the directory where the experiment files are located
        """

        # TOOD: Why is the logger not recognized here opposing to optimizer.py
        #logging.info("Interp2DRunner: Loading data...")
        print "Interp2DRunner: Loading data..."

        list_experiments_data = []
        for path in glob.glob(os.path.join(dir_path, "*.h5")):
            list_experiments_data.append(Experiment.load(path))

        #logging.info("Interp2DRunner: Data loaded.")
        print "Interp2DRunner: Data loaded."

        return cls(list_experiments_data)

    def put(self, experiment):
        self._list_experiments.append(experiment)

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass

    def is_alive(self):
        return False

    def join(self):
        pass

    def get_results(self):
        list_experiments = list(self._list_experiments)
        for experiment in list_experiments:
            experiment._set_kratios(self._calc_kratios(experiment))

        self._list_experiments = []

        return list_experiments

    def report(self):
        completed = len(self._list_experiments)
        return completed, 0, ''

    def _calc_kratios(self, experiment):
        x = experiment.get_values()

        return self._spline(x[0], x[1])

    def _collect_data(self, list_experiments_data):
        xs, ys, zs = [], [], []
        for experiment in list_experiments_data:
            x = experiment.get_values()

            if len(x) <> 2:
                raise ValueError, "Number of paramaters (%s) is not equal to two." % len(x)

            xs.append(x[0])
            ys.append(x[1])
            zs.append(experiment.get_kratios())

        if len(xs) <> len(zs) or len(ys) <> len(zs):
            raise ValueError, 'Wrong data format:' \
                + ' lengths of individual coordinate lists do not match.'

        return {'xs': xs, 'ys': ys, 'zs': zs}

    def _get_spline(self, data):
        xs = data['xs']
        ys = data['ys']
        zs = data['zs']

        splines = []
        for i in range(0, len(zs[0])):
            splines.append(SmoothBivariateSpline(xs, ys, [z[i] for z in zs]))

        def _spline(x, y):
            return [spline(x, y)[0][0] for spline in splines]

        return _spline

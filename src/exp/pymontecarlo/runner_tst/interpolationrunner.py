#!/usr/bin/env python
"""
================================================================================
:mod:`interpolationrunner` -- Calculate intensities based on interpolated data
================================================================================

.. module:: interpolationrunner
   :synopsis: Calculate intensities based on interpolated data

.. inheritance-diagram:: pymontecarlo.runner.interpolationrunner

"""
# Script information for the file.
__author__ = "Niklas Mevenkamp"
__email__ = "niklas.mevenkamp@gmx.net"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Niklas Mevenkamp"
__license__ = "GPL v3"

# Standard library modules
import os
from Queue import Empty

# Third party modules
from scipy.interpolate.interpolate import interp2d

# Local modules
from pymontecarlo.runner.base import _Runner
from pymontecarlo.output.results import Results
from pymontecarlo.output.result import create_intensity_dict



class Interp2DRunner(_Runner):
    def __init__(self, results, experiment):
        """
        Creates a new interpolation runner that can interpolate data from results that were produced
        using the Experiment class.
        Note: Interpolation is only available for experiments with 2 parameters.
        
        :arg results: either a list of results objects or a path to a directory containing results objects
            in a format readable by pymontecarlo.output.results.Results.load()
        :arg experiment: experiment that was used to create the results files
        """
        _Runner.__init__(self, program=None)
        
        self.results = results
        self.experiment = experiment
        
        self.data = self._collect_data(self.results, self.experiment)
        self.spline = self._get_spline(self.data)
        
    def start(self):
        list_options = []
        while True:
            try:
                list_options.append(self._queue_options.get_nowait())
            except Empty:
                break
            
        if list_options:
            list_results = []
            for options in list_options:
                list_results.append(Results(options))
            
            i = -1
            for j, measurement in enumerate(self.experiment._measurements):
                transitions = measurement.get_transitions()
                results = list_results[j]
                
                x = [getter(results.options.geometry) for getter in self.experiment.parameters_getters]
                if len(x) <> 2:
                    raise ValueError, "Number of paramaters is not equal to two (length is %s)." % len(x)
                z = self.spline(x[0], x[1])
                
                intensities = {}
                for transition in transitions:
                    i += 1
                    intensities.update(create_intensity_dict(transition, et=(z[i], 0.0)))
                    
                self._queue_results.put(results)
                self._queue_options.task_done()
    
    def stop(self):
        pass
    
    def close(self):
        pass
        
    def _collect_data(self, results, experiment):
        xs, ys = [], []
        list_results = []
        
        if os.path.isdir(results):
            for filename in os.listdir(results):
                if filename.endswith(".h5"):
                    list_results.append(Results.load(results + filename))
        else:
            list_results = results
        
        xs_used = []
        for results in list_results:
            x = [getter(results.options.geometry) for getter in self.experiment.parameters_getters]
            if len(x) <> 2:
                raise ValueError, "Number of paramaters is not equal to two (length is %s)." % len(x)
            if not x in xs_used:
                xs_used.append(x)
                xs.append(x[0])
                ys.append(x[1])
        
        zs = experiment.extract_unknown_intensities(list_results)
        
        return {'xs': xs, 'ys': ys, 'zs': zs}
    
    def _get_spline(self, data):
        xs = data['xs']
        ys = data['ys']
        zs = data['zs']
        
        splines = []
        for i in range(0,len(zs[0])):
            splines.append(interp2d(xs, ys, [z[i] for z in zs], kind='cubic'))
        
        def _spline(x, y):
            return [spline(x, y)[0] for spline in splines]
        
        return _spline
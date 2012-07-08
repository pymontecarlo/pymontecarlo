#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Worker for quantification
================================================================================

.. module:: worker
   :synopsis: Worker for quantification

.. inheritance-diagram:: pymontecarlo.quant.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import copy
import logging
import threading
import time
import math

# Third party modules.

# Local modules.
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.output.results import Results as SimResults
from pymontecarlo.quant.output.results import Results as QuantResult

# Globals and constants variables.

class Worker(threading.Thread):
    def __init__(self, queue_measurements, runner, iterator_class, outputdir,
                       max_iterations=50, convergence_limit=1e-5,
                       overwrite=True, **kwargs):
        threading.Thread.__init__(self)

        self._queue_measurements = queue_measurements

        self._runner = runner

        self._iterator_class = iterator_class
        self._kwargs = kwargs

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        self._workdir = runner.outputdir

        if max_iterations < 1:
            raise ValueError, 'Maximum number of iterations must be greater or equal to 1'
        self._max_iterations = max_iterations

        if convergence_limit <= 0.0:
            raise ValueError, 'Convergence limit must be greater than 0.0'
        self._convergence_limit = convergence_limit

        self._overwrite = overwrite

        self._reset()

    def _reset(self):
        """
        Resets the worker. This method is called before starting a run.
        """
        self._progress = 0.0
        self._status = ''
        self._should_continue = True

    def run(self):
        """
        Creates and runs all simulations in the options queue.
        The results from the simulations are then saved in the *output directory*.
        """
        while True:
            try:
                self._reset()

                self._progress = 0.0
                self._status = 'Starting'

                # Retrieve measurement
                measurement = self._queue_measurements.get()

                # Check if results already exists
                name = measurement.options.name
                zipfilepath = os.path.join(self._outputdir, name + ".zip")
                if os.path.exists(zipfilepath) and not self._overwrite:
                    logging.info('Skipping %s as measurement results already exists', name)
                    self._queue_measurements.task_done()
                    continue

                # Run
                start_time_s = time.time()
                iterator = self._run(measurement)
                end_time_s = time.time()

                # Save results
                logging.debug('Started saving results')
                elapsed_time_s = end_time_s - start_time_s
                self._save_results(measurement, iterator, elapsed_time_s, zipfilepath)
                logging.debug('Results saved at %s', zipfilepath)

                self._progress = 1.0
                self._status = 'Completed'

                self._queue_measurements.task_done()
            except Exception:
                self.stop()
                self._queue_measurements.raise_exception()

    def _run(self, measurement):
        """
        Runs quantification from the specified measurement.
        """
        # Extract variables from measurement
        options = measurement.options
        unknown_body = measurement.unknown_body
        detector_key = measurement.detector_key
        transitions = measurement.get_transitions()
        standards = measurement.get_standards()
        rules = measurement.get_rules()

        # Initial guess of composition
        initial_composition = self._calculate_initial_composition(measurement)
        self._apply_composition_rules(rules, initial_composition)

        # Create iterator
        iterator = self._iterator_class(measurement.get_kratios(),
                                        initial_composition,
                                        **self._kwargs)

        # Standards
        self._status = 'Simulate standards'
        self._run_standards(options, standards)
        stdintensities = self._read_standard_intensities(detector_key, transitions)

        composition = iterator[0]
        logging.debug('Initial composition: %s', composition)

        # Iteration
        index = 0
        while index < self._max_iterations and self._should_continue:
            # Run next iteration
            index += 1
            self._progress = float(index) / self._max_iterations

            self._status = 'Simulate iteration'
            self._run_iteration(index, composition, options, unknown_body, rules)
            unkintensities = \
                self._read_iteration_intensities(index, detector_key, transitions)

            # Calculate new k-ratios
            kratios = {}
            for z, unkintensity in unkintensities.iteritems():
                unkval, unkunc = unkintensity
                stdval, stdunc = stdintensities[z]

                kratioval = unkval / stdval
                kratiounc = kratioval * math.sqrt((unkunc / unkval) ** 2 + \
                                                  (stdunc / stdval) ** 2)

                kratios[z] = kratioval, kratiounc

            # Iterate for new composition
            self._status = 'Calculate new composition'
            previous_composition = composition
            composition = iterator.next(kratios)

            # Check for convergence
            residuals = {}
            for z, wf in composition.iteritems():
                if z in rules: continue # skip element that have rules

                residual = abs(wf - previous_composition.get(z, 0.0))
                if residual > self._convergence_limit:
                    residuals[z] = residual

            logging.debug('Iteration %i - estimate: %s', index, composition)
            logging.debug('Iteration %i - residual: %s', index, residuals)

            if not residuals:
                break

        return iterator

    def _apply_composition_rules(self, rules, composition):
        for rule in rules:
            rule.update(composition)

    def _normalize_composition(self, composition):
        total = sum(composition.values())

        for z, wf in composition.iteritems():
            composition[z] = wf / total

    def _calculate_initial_composition(self, measurement):
        """
        Compute the initial weight fraction assuming a ZAF of 1.0 for each 
        element.
        This method is used in DTSA-II.
    
        :return: composition
        """
        kratios = measurement.get_kratios()
        standards = measurement.get_standards()

        composition = {}
        for z, kratio in kratios.iteritems():
            wf = standards[z].composition[z]
            composition[z] = kratio[0] * wf

        return composition

    def _run_standards(self, options, standards):
        """
        Runs all the standards.
        """
        for z, material in standards.iteritems():
            ops = copy.deepcopy(options)

            ops.name = 'std%i' % z
            ops.geometry = Substrate(material)

            self._runner.put(ops)

        self._runner.join()

    def _run_iteration(self, index, composition, options, unknown_body, rules):
        """
        Normalizes the composition, assigns it to the unknown body and then
        run the simulation.
        """
        composition2 = composition.copy()
        self._apply_composition_rules(rules, composition2)
        self._normalize_composition(composition2)

        options.name = 'iteration%i' % index
        unknown_body.material.composition = composition2

        self._runner.put(options)
        self._runner.join()

    def _read_standard_intensities(self, detector_key, transitions):
        """
        Reads the intensities of all standards.
        """
        intensities = {}

        for transition in transitions:
            filename = 'std%i.zip' % transition.z
            filepath = os.path.join(self._workdir, filename)
            results = SimResults.load(filepath)

            val, unc = results[detector_key].intensity(transition)
            intensities[transition.z] = (val, unc)

        return intensities

    def _read_iteration_intensities(self, index, detector_key, transitions):
        """
        Reads the intensities of iteration *index*.
        """
        intensities = {}

        filename = 'iteration%i.zip' % index
        filepath = os.path.join(self._workdir, filename)
        results = SimResults.load(filepath)

        for transition in transitions:
            try:
                val, unc = results[detector_key].intensity(transition)
            except ValueError:
                val = 0.0
                unc = 0.0
            intensities[transition.z] = (val, unc)

        return intensities

    def _save_results(self, measurement, iterator, elapsed_time_s, zipfilepath):
        """
        Generates the results from the measurement outputs after the measurement 
        was run and then save them at the specified location.
        """
        # Compositions
        rules = measurement.get_rules()

        compositions = []
        for composition in map(dict, iterator): # copy
            self._apply_composition_rules(rules, composition)
            compositions.append(composition)

        # Create results
        results = QuantResult(compositions, elapsed_time_s,
                              self._max_iterations, self._convergence_limit,
                              iterator.__class__.__name__)
        results.save(zipfilepath)

    def stop(self):
        """
        Stops worker.
        """
        self._should_continue = False
        self._status = 'Stopping after next iteration'

    def report(self):
        """
        Returns a tuple of:
        
          * the percent of number of iterations run or running out of the 
            maximum number of iterations
          * text indicating the status of the current running quantification
        """
        return self._progress, self._status

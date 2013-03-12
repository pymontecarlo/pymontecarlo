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
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.output.results import Results as SimResults
from pymontecarlo.runner.runner import Runner as SimRunner
from pymontecarlo.quant.output.results import Results as QuantResults

# Globals and constants variables.
_DETECTOR_KEY = 'xrays'

class Worker(threading.Thread):
    def __init__(self, queue_measurements, worker_class,
                 iterator_class, convergor_class, calculator_class,
                 outputdir, workdir=None,
                 max_iterations=50, overwrite=True, **kwargs):
        threading.Thread.__init__(self)

        # Setup work directory
        if workdir is not None and not os.path.isdir(workdir):
            raise ValueError, 'Work directory (%s) is not a directory' % workdir
        self._workdir = workdir

        if self._workdir is None:
            self._workdir = tempfile.mkdtemp()
            self._user_defined_workdir = False
            logging.debug('Temporary work directory: %s', self._workdir)
        else:
            self._user_defined_workdir = True

        # Create runner
        self._runner = SimRunner(worker_class, self._workdir,
                                 workdir=None, overwrite=True, nbprocesses=1)

        # Setup variables
        self._queue_measurements = queue_measurements

        self._iterator_class = iterator_class
        self._convergor_class = convergor_class
        self._calculator_class = calculator_class
        self._kwargs = kwargs

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        if max_iterations < 0:
            raise ValueError, 'Maximum number of iterations must be greater or equal to 0'
        self._max_iterations = max_iterations

        self._overwrite = overwrite

        self._reset()

    def _reset(self):
        """
        Resets the worker. This method is called before starting a run.
        """
        self._progress = 0.0
        self._status = ''
        self._should_continue = True

    def start(self):
        self._runner.start()
        threading.Thread.start(self)

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
                iterator, convergor = self._run(measurement)
                end_time_s = time.time()

                # Save results
                logging.debug('Started saving results')
                elapsed_time_s = end_time_s - start_time_s
                self._save_results(measurement, iterator, convergor,
                                   elapsed_time_s, zipfilepath)
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
        detector = measurement.detector
        transitions = measurement.get_transitions()
        experimental_kratios = measurement.get_kratios()
        standards = measurement.get_standards()
        rules = measurement.get_rules()

        # Initial guess of composition
        initial_composition = \
            self._calculate_initial_composition(experimental_kratios, standards)
        self._apply_composition_rules(rules, initial_composition)

        # Standards
        self._status = 'Simulate standards'
        self._run_standards(options, unknown_body, detector, standards)
        stdintensities = \
            self._read_standard_intensities(transitions)

        # Create iterator
        iterator = self._iterator_class(experimental_kratios,
                                        initial_composition, **self._kwargs)

        # Create convergor
        convergor = self._convergor_class(experimental_kratios,
                                          initial_composition, **self._kwargs)

        # Create calculator
        calculator = \
            self._calculator_class(measurement, stdintensities, **self._kwargs)

        composition = iterator[0]
        logging.debug('Initial composition: %s', composition)

        # Iterative loop
        index = 0
        while index < self._max_iterations and self._should_continue:
            # Run next iteration
            index += 1
            self._progress = float(index) / self._max_iterations

            self._status = 'Simulate iteration'
            self._run_iteration(index, composition, options,
                                unknown_body, detector, rules)
            unkintensities = \
                self._read_iteration_intensities(index, transitions)

            # Calculate new k-ratios
            self._status = 'Calculate k-ratios'
            kratios = calculator.calculate(unkintensities)

            # Iterate for new composition
            self._status = 'Calculate new composition'
            composition = iterator.next(kratios)

            # Check for convergence
            convergor.add_iteration(kratios, composition)
            if convergor.has_converged():
                break

        return iterator, convergor

    def _apply_composition_rules(self, rules, composition):
        for rule in rules:
            rule.update(composition)

    def _normalize_composition(self, composition):
        total = sum(composition.values())

        for z, wf in composition.iteritems():
            composition[z] = wf / total

    def _calculate_initial_composition(self, kratios, standards):
        """
        Compute the initial weight fraction assuming a ZAF of 1.0 for each 
        element.
        This method is used in DTSA-II.
    
        :return: composition
        """
        composition = {}
        for z, kratio in kratios.iteritems():
            wf = standards[z].material.composition[z]
            composition[z] = kratio[0] * wf

        return composition

    def _run_standards(self, options, unknown_body, detector, standards):
        """
        Runs all the standards.
        """
        for z, geometry in standards.iteritems():
            ops = copy.deepcopy(options)

            ops.name = 'std%i' % z

            ops.detectors.clear()
            ops.detectors[_DETECTOR_KEY] = detector

            ops.geometry = geometry

            self._runner.put(ops)

        self._runner.join()

    def _run_iteration(self, index, composition, options,
                       unknown_body, detector, rules):
        """
        Normalizes the composition, assigns it to the unknown body and then
        run the simulation.
        """
        composition2 = composition.copy()
        self._apply_composition_rules(rules, composition2)
        self._normalize_composition(composition2)

        options.name = 'iteration%i' % index

        options.detectors.clear()
        options.detectors[_DETECTOR_KEY] = detector

        unknown_body.material.composition = composition2

        self._runner.put(options)
        self._runner.join()

    def _read_standard_intensities(self, transitions):
        """
        Reads the intensities of all standards.
        """
        intensities = {}

        for transition in transitions:
            filename = 'std%i.h5' % transition.z
            filepath = os.path.join(self._workdir, filename)
            results = SimResults.load(filepath)

            val, unc = results[_DETECTOR_KEY].intensity(transition)
            intensities[transition.z] = (val, unc)

        return intensities

    def _read_iteration_intensities(self, index, transitions):
        """
        Reads the intensities of iteration *index*.
        """
        intensities = {}

        filename = 'iteration%i.h5' % index
        filepath = os.path.join(self._workdir, filename)
        results = SimResults.load(filepath)

        for transition in transitions:
            try:
                val, unc = results[_DETECTOR_KEY].intensity(transition)
            except ValueError:
                val = 0.0
                unc = 0.0
            intensities[transition.z] = (val, unc)

        return intensities

    def _save_results(self, measurement, iterator, convergor,
                      elapsed_time_s, zipfilepath):
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
        results = QuantResults(compositions, elapsed_time_s,
                               self._max_iterations, iterator, convergor)
        results.save(zipfilepath)

    def stop(self):
        """
        Stops worker.
        """
        self._runner.stop()

        self._should_continue = False
        self._status = 'Stopping after next iteration'

        # Cleanup working directory if needed
        if not self._user_defined_workdir:
            shutil.rmtree(self._workdir, ignore_errors=True)
            logging.debug('Removed temporary work directory: %s', self._workdir)
            self._workdir = None

    def report(self):
        """
        Returns a tuple of:
        
          * the percent of number of iterations run or running out of the 
            maximum number of iterations
          * text indicating the status of the current running quantification
        """
        return self._progress, self._status

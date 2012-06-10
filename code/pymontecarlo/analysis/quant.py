#!/usr/bin/env python
"""
================================================================================
:mod:`quant` -- Quantitative iteration to calculate the composition
================================================================================

.. module:: quant
   :synopsis: Quantitative iteration to calculate the composition

.. inheritance-diagram:: iteration

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

# Third party modules.

# Local modules.
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.output.results import Results

# Globals and constants variables.

class Quantification(threading.Thread):

    def __init__(self, runner, iterator_class, measurement,
                 max_iterations=50, convergence_limit=1e-5):
        threading.Thread.__init__(self)

        self._runner = runner
        self._outputdir = runner.outputdir

        initial_composition = self._calculate_initial_composition(measurement)
        self._iterator = iterator_class(measurement.get_kratios(),
                                        initial_composition)

        self._options = measurement.options
        self._unknown_body = measurement.unknown_body
        self._detector_key = measurement.detector_key
        self._transitions = measurement.get_transitions()
        self._standards = measurement.get_standards()
        self._rules = measurement.get_rules()

        if max_iterations < 1:
            raise ValueError, 'Maximum number of iterations must be greater or equal to 1'
        self._max_iterations = max_iterations

        if convergence_limit <= 0.0:
            raise ValueError, 'Convergence limit must be greater than 0.0'
        self._convergence_limit = convergence_limit

        self._status = ''

    def start(self):
        self._should_continue = True
        self._iterator.reset()

        threading.Thread.start(self)
        self._status = 'Started'

    def run(self):
        # Standards
        self._status = 'Simulate standards'
        self._run_standards()
        stdintensities = self._read_standard_intensities()

        composition = self._iterator[0]
        logging.debug('Initial composition: %s', composition)

        # Iteration
        index = 0
        while index < self._max_iterations and self._should_continue:
            # Run next iteration
            index += 1

            self._status = 'Simulate iteration'
            self._run_iteration(index, composition)
            unkintensities = \
                self._read_iteration_intensities(index)

            # Calculate new k-ratios
            kratios = {}
            for z, unkintensity in unkintensities.iteritems():
                stdintensity = stdintensities[z]
                kratios[z] = unkintensity / stdintensity

            # Iterate for new composition
            self._status = 'Calculate new composition'
            previous_composition = composition
            composition = self._iterator.next(kratios)

            # Check for convergence
            residuals = {}
            for z, wf in composition.iteritems():
                if z in self._rules: continue # skip element that have rules

                residual = abs(wf - previous_composition.get(z, 0.0))
                if residual > self._convergence_limit:
                    residuals[z] = residual

            logging.debug('Iteration %i - estimate: %s', index, composition)
            logging.debug('Iteration %i - residual: %s', index, residuals)

            if not residuals:
                break

        self._status = 'Completed'

    def _apply_composition_rules(self, composition):
        for rule in self._rules:
            rule.update(composition)

    def _normalize_composition(self, composition):
        total = sum(composition.values())

        for z, wf in composition.iteritems():
            composition[z] = wf / total

    def _calculate_initial_composition(self, measurement):
        """
        Compute the initial weight fraction.
    
        Using method reported in Heinrich (1972).
    
        Reference: Heinrich, K. F. J. Errors in theoretical correction systems
        in quantitative electron probe microanalysis.
        Synopsis Analytical Chemistry, 1972, 44, 350-354 [heinrich1972a]
    
        .. math:
             C'_{0A} = \frac{k_{A}}{\sum k_{i}}.
    
        :arg kratios: k-ratios for each element given as a :class:`dict` where 
            the keys are atomic numbers and the values are experimental k-ratios.
        :type kratios: :class:`dict`
    
        :return: composition
        """
        kratios = measurement.get_kratios()
        rules = measurement.get_rules()

        total_kratio = sum(kratios.values()) + 0.1 * len(rules)

        composition = {}
        for z, kratio in kratios.iteritems():
            composition[z] = kratio / total_kratio

        return composition

    def _run_standards(self):
        """
        Runs all the standards.
        """
        self._runner.start()

        for z, material in self._standards.iteritems():
            ops = copy.deepcopy(self._options)

            ops.name = 'std%i' % z
            ops.geometry = Substrate(material)

            self._runner.put(ops)

        self._runner.join()

    def _run_iteration(self, index, composition):
        """
        Normalizes the composition, assigns it to the unknown body and then
        run the simulation.
        """
        composition2 = composition.copy()
        self._apply_composition_rules(composition2)
        self._normalize_composition(composition2)

        self._runner.start()

        self._options.name = 'iteration%i' % index
        self._unknown_body.material.composition = composition2

        self._runner.put(self._options)
        self._runner.join()

    def _read_standard_intensities(self):
        """
        Reads the intensities of all standards.
        """
        intensities = {}

        for transition in self._transitions:
            filename = 'std%i.zip' % transition.z
            filepath = os.path.join(self._outputdir, filename)
            results = Results.load(filepath)

            val, _unc = results[self._detector_key].intensity(transition)
            intensities[transition.z] = val

        return intensities

    def _read_iteration_intensities(self, index):
        """
        Reads the intensities of iteration *index*.
        """
        intensities = {}

        filename = 'iteration%i.zip' % index
        filepath = os.path.join(self._outputdir, filename)
        results = Results.load(filepath)

        for transition in self._transitions:
            try:
                val, _unc = results[self._detector_key].intensity(transition)
            except ValueError:
                val = 0.0
            intensities[transition.z] = val

        return intensities

    def report(self):
        """
        Returns a tuple of:
        
          * counter of completed iterations
          * the progress of teh currently running simulation 
              (between 0.0 and 1.0)
          * text indicating the status of the iteration process
        """
        iterations = len(self._iterator) + 1
        _completed, progress, _status = self._runner.report()
        return iterations, progress, self._status

    def stop(self):
        """
        Stops the quantification after the next iteration.
        """
        self._should_continue = False
        self._status = 'Stopping after next iteration'
        self.join()

    def get_last_composition(self):
        """
        Returns the last composition from the iteration.
        Note that this composition can also be directly retrieved from 
        the specified unknown body material.
        """
        composition = self._iterator[-1].copy()
        self._apply_composition_rules(composition)
        return composition

#def run():
#    logging.getLogger().setLevel(logging.DEBUG)
#
#    from pymontecarlo.analysis.iterator import Heinrich1972Iterator
#    from pymontecarlo.program.pap.runner.worker import Worker
#    from pymontecarlo.input.options import Options
#    from pymontecarlo.input.detector import PhotonIntensityDetector
#    from pymontecarlo.util.transition import from_string
#    from math import radians
#    from pymontecarlo.runner.runner import Runner
#    import time
#    from pymontecarlo.analysis.measurement import Measurement
#    from pymontecarlo.analysis.rule import ElementByDifference
#
#    iterator_class = Heinrich1972Iterator
#    worker_class = Worker
#
#    options = Options('PAP')
#    options.beam.energy_eV = 20000
#    options.detectors['xray'] = \
#        PhotonIntensityDetector((radians(52.5), radians(52.5)), (0.0, radians(360.0)))
#
#    m = Measurement(options, options.geometry.body, 'xray')
#    m.add_kratio(from_string('Cu Ka'), 0.2470)
#    m.add_rule(ElementByDifference(79))
#
#    outputdir = '/tmp/quant'
#    runner = Runner(worker_class, outputdir)
#
#    q = Quantification(runner, iterator_class, m)
#
#    q.start()
#
#    while q.is_alive():
#        print q.report()
#        time.sleep(1)
#
#    print q.get_last_composition()
#
#run()

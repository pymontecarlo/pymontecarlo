#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil
from math import radians

# Third party modules.
from nose.plugins.attrib import attr

# Local modules.
#from pymontecarlo.testcase import TestCase

from pymontecarlo.quant.runner.runner import Runner
from pymontecarlo.quant.runner.iterator import Heinrich1972Iterator
from pymontecarlo.quant.runner.convergor import CompositionConvergor
from pymontecarlo.quant.runner.calculator import SimpleCalculator
from pymontecarlo.quant.input.measurement import Measurement
from pymontecarlo.quant.input.rule import ElementByDifferenceRule
from pymontecarlo.quant.output.results import Results

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.limit import ShowersLimit

from pymontecarlo.program.pap.runner.worker import Worker

from pymontecarlo.util.transition import Ka

# Globals and constants variables.

class TestRunner(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        iterator_class = Heinrich1972Iterator
        convergor_class = CompositionConvergor
        calculator_class = SimpleCalculator
        worker_class = Worker

        options = Options('PAP')
        options.beam.energy_eV = 20000
        options.limits.add(ShowersLimit(100))

        detector = PhotonIntensityDetector((radians(50), radians(55)),
                                          (0.0, radians(360.0)))

        self.m = Measurement(options, options.geometry.body, detector)
        self.m.add_kratio(Ka(29), 0.2470)
        self.m.add_rule(ElementByDifferenceRule(79))

        self.outputdir = tempfile.mkdtemp()

        self.runner = Runner(worker_class, iterator_class, convergor_class,
                             calculator_class, self.outputdir, limit=0.1)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        shutil.rmtree(self.outputdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    @attr('slow')
    def testrun(self):
        self.runner.start()
        self.runner.put(self.m)
        self.runner.join()

        filepath = os.path.join(self.outputdir, 'PAP.zip')
        results = Results.load(filepath)

        composition = results.compositions[-1]
        self.assertAlmostEqual(0.21069, composition[29], 4)
        self.assertAlmostEqual(0.78931, composition[79], 4)

        self.assertEqual(1, results.iterations)
        self.assertEqual(1, len(results.compositions))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

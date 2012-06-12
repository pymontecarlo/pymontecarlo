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
import tempfile
import shutil
from math import radians

# Third party modules.
from nose.plugins.attrib import attr

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.analysis.quant import Quantification

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.program.pap.runner.worker import Worker
from pymontecarlo.runner.runner import Runner
from pymontecarlo.analysis.measurement import Measurement
from pymontecarlo.analysis.rule import ElementByDifference
from pymontecarlo.analysis.iterator import Heinrich1972Iterator
from pymontecarlo.util.transition import Ka

# Globals and constants variables.

class TestQuantification(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        iterator_class = Heinrich1972Iterator
        worker_class = Worker

        options = Options('PAP')
        options.beam.energy_eV = 20000
        options.detectors['xray'] = \
            PhotonIntensityDetector((radians(52.5), radians(52.5)),
                                    (0.0, radians(360.0)))

        m = Measurement(options, options.geometry.body, 'xray')
        m.add_kratio(Ka(29), 0.2470)
        m.add_rule(ElementByDifference(79))

        self._outputdir = tempfile.mkdtemp()
        runner = Runner(worker_class, self._outputdir)

        self.q = Quantification(runner, iterator_class, m,
                                convergence_limit=0.1)

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self._outputdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    @attr('slow')
    def testrun(self):
        self.q.start()
        self.q.join()

        composition = self.q.get_last_composition()

        self.assertAlmostEqual(0.21013, composition[29], 4)
        self.assertAlmostEqual(0.78987, composition[79], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

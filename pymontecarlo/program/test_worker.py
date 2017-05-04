#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.mock import WorkerMock
from pymontecarlo.simulation import Simulation
from pymontecarlo.util.future import Token

# Globals and constants variables.

class TestWorker(TestCase):

    def setUp(self):
        super().setUp()

        self.w = WorkerMock()

        self.outputdir = self.create_temp_dir()

    def testrun(self):
        token = Token()
        options = self.create_basic_options()
        simulation = Simulation(options)
        self.w.run(token, simulation, self.outputdir)

        self.assertAlmostEqual(1.0, token.progress)
        self.assertEqual('Done', token.status)
        self.assertFalse(token.cancelled())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

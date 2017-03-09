#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase, WorkerMock
from pymontecarlo.simulation import Simulation

# Globals and constants variables.

class TestWorker(TestCase):

    def setUp(self):
        super().setUp()

        self.w = WorkerMock()

        self.outputdir = self.create_temp_dir()

    def testrun(self):
        options = self.create_basic_options()
        simulation = Simulation(options)
        self.w.run(simulation, self.outputdir)

        self.assertAlmostEqual(1.0, self.w.progress)
        self.assertEqual('Done', self.w.status)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

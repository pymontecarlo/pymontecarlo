#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult

# Globals and constants variables.

class TestSimulation(TestCase):

    def setUp(self):
        super().setUp()

        self.sim = self.create_basic_simulation()

    def testfind_result(self):
        results = self.sim.find_result(EmittedPhotonIntensityResult)
        self.assertEqual(1, len(results))

    def testidentifier(self):
        print(self.sim.identifier)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

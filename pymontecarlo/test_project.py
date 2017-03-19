#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult

# Globals and constants variables.

class TestProject(TestCase):

    def setUp(self):
        super().setUp()

        self.p = self.create_basic_project()

    def testskeleton(self):
        self.assertEqual(3, len(self.p.simulations))

    def testcreate_datarows(self):
        datarows = self.p.create_datarows(only_different_options=True)
        self.assertEqual(3, len(datarows))

        self.assertEqual(2, len(datarows[0]))
        self.assertEqual(2, len(datarows[1]))
        self.assertEqual(2, len(datarows[2]))

    def testcreate_datarows_withresults(self):
        datarows = self.p.create_datarows(only_different_options=True,
                                          result_classes=[EmittedPhotonIntensityResult])
        self.assertEqual(3, len(datarows))

        self.assertEqual(9, len(datarows[0]))
        self.assertEqual(9, len(datarows[1]))
        self.assertEqual(9, len(datarows[2]))

        datarows = self.p.create_datarows(only_different_options=True,
                                          result_classes=[GeneratedPhotonIntensityResult])
        self.assertEqual(3, len(datarows))

        self.assertEqual(2, len(datarows[0]))
        self.assertEqual(2, len(datarows[1]))
        self.assertEqual(5, len(datarows[2]))

        datarows = self.p.create_datarows(only_different_options=True,
                                          result_classes=[EmittedPhotonIntensityResult,
                                                          GeneratedPhotonIntensityResult])
        self.assertEqual(3, len(datarows))

        self.assertEqual(9, len(datarows[0]))
        self.assertEqual(9, len(datarows[1]))
        self.assertEqual(12, len(datarows[2]))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

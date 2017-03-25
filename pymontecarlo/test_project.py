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
        self.assertEqual(2, len(self.p.result_classes))

    def testcreate_options_datarows(self):
        datarows = self.p.create_options_datarows(only_different_columns=True)
        self.assertEqual(3, len(datarows))

        self.assertEqual(2, len(datarows[0]))
        self.assertEqual(2, len(datarows[1]))
        self.assertEqual(2, len(datarows[2]))

    def testcreate_results_datarows_withresults(self):
        result_classes = [EmittedPhotonIntensityResult]
        datarows = self.p.create_results_datarows(result_classes)
        self.assertEqual(3, len(datarows))

        self.assertEqual(7, len(datarows[0]))
        self.assertEqual(7, len(datarows[1]))
        self.assertEqual(7, len(datarows[2]))

        result_classes = [GeneratedPhotonIntensityResult]
        datarows = self.p.create_results_datarows(result_classes)
        self.assertEqual(3, len(datarows))

        self.assertEqual(0, len(datarows[0]))
        self.assertEqual(0, len(datarows[1]))
        self.assertEqual(3, len(datarows[2]))

        result_classes = [EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult]
        datarows = self.p.create_results_datarows(result_classes)
        self.assertEqual(3, len(datarows))

        self.assertEqual(7, len(datarows[0]))
        self.assertEqual(7, len(datarows[1]))
        self.assertEqual(10, len(datarows[2]))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

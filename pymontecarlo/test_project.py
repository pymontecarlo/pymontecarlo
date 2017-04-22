#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult
from pymontecarlo.project import Project

# Globals and constants variables.

class TestProject(TestCase):

    def setUp(self):
        super().setUp()

        self.p = self.create_basic_project()

    def testskeleton(self):
        self.assertEqual(3, len(self.p.simulations))
        self.assertEqual(2, len(self.p.result_classes))

    def testcreate_options_dataframe(self):
        df = self.p.create_options_dataframe(only_different_columns=False)
        self.assertEqual(3, len(df))

    def testcreate_options_dataframe_only_different_columns(self):
        df = self.p.create_options_dataframe(only_different_columns=True)
        self.assertEqual(3, len(df))

        self.assertEqual(2, len(df.loc[0]))
        self.assertEqual(2, len(df.loc[1]))
        self.assertEqual(2, len(df.loc[2]))

    def testcreate_results_dataframe(self):
        df = self.p.create_results_dataframe()
        self.assertEqual(3, len(df))

        self.assertEqual(20, len(df.loc[0]))
        self.assertEqual(20, len(df.loc[1]))
        self.assertEqual(20, len(df.loc[2]))

        self.assertEqual(14, len(df.loc[0].dropna()))
        self.assertEqual(14, len(df.loc[1].dropna()))
        self.assertEqual(20, len(df.loc[2].dropna()))

    def testcreate_results_dataframe_with_results(self):
        result_classes = [EmittedPhotonIntensityResult]
        df = self.p.create_results_dataframe(result_classes)
        self.assertEqual(3, len(df))

        self.assertEqual(14, len(df.loc[0]))
        self.assertEqual(14, len(df.loc[1]))
        self.assertEqual(14, len(df.loc[2]))

    def testcreate_results_dataframe_with_missing_results(self):
        result_classes = [GeneratedPhotonIntensityResult]
        df = self.p.create_results_dataframe(result_classes)
        self.assertEqual(3, len(df))

        self.assertEqual(6, len(df.loc[0]))
        self.assertEqual(6, len(df.loc[1]))
        self.assertEqual(6, len(df.loc[2]))

        self.assertEqual(0, len(df.loc[0].dropna()))
        self.assertEqual(0, len(df.loc[1].dropna()))
        self.assertEqual(6, len(df.loc[2].dropna()))

    def testcreate_results_dataframe_with_two_results(self):
        result_classes = [EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult]
        df = self.p.create_results_dataframe(result_classes)
        self.assertEqual(3, len(df))

        self.assertEqual(20, len(df.loc[0]))
        self.assertEqual(20, len(df.loc[1]))
        self.assertEqual(20, len(df.loc[2]))

        self.assertEqual(14, len(df.loc[0].dropna()))
        self.assertEqual(14, len(df.loc[1].dropna()))
        self.assertEqual(20, len(df.loc[2].dropna()))

    def testread_write(self):
        filepath = os.path.join(self.create_temp_dir(), 'project.h5')
        self.p.write(filepath)
        p = Project.read(filepath)
        self.assertEqual(3, len(p.simulations))
        self.assertEqual(2, len(p.result_classes))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

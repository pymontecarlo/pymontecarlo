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
from zipfile import ZipFile

# Third party modules.

# Local modules.
from pymontecarlo.quant.output.results import Results

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestResults(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        # Temporary directory
        self.tmpdir = tempfile.mkdtemp()

        compositions = [{29:0.5, 79:0.5}, {29:0.2, 79:0.8}]
        self.results = Results(compositions, 123.456, 12, 'TestIterator', 'TestConvergor')

        relpath = os.path.join('..', '..', 'testdata', 'quant_results.zip')
        self.results_zip = Files.getCurrentModulePath(__file__, relpath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testload(self):
        results = Results.load(self.results_zip)

        self.assertEqual(2, results.iterations)
        self.assertEqual(2, len(results.compositions))
        self.assertAlmostEqual(0.5, results.compositions[0][29], 4)
        self.assertAlmostEqual(0.5, results.compositions[0][79], 4)
        self.assertAlmostEqual(0.2, results.compositions[-1][29], 4)
        self.assertAlmostEqual(0.8, results.compositions[-1][79], 4)

        self.assertAlmostEqual(0.0, results.compositions[-1][99], 4) # test defaultdict

        self.assertAlmostEqual(123.456, results.elapsed_time_s, 4)
        self.assertEqual(12, results.max_iterations)
        self.assertEqual('TestIterator', results.iterator)
        self.assertEqual('TestConvergor', results.convergor)

    def testsave(self):
        zipfilepath = os.path.join(self.tmpdir, 'results.zip')
        self.results.save(zipfilepath)

        with open(zipfilepath, 'r') as fp:
            zipfile = ZipFile(fp, 'r')

            namelist = zipfile.namelist()
            self.assertTrue('compositions.csv' in namelist)
            self.assertTrue('stats.cfg' in namelist)

            zipfile.close()

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

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
from zipfile import ZipFile
import os

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.output.results import Results
from pymontecarlo.output.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestResults(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        # Temporary directory
        self.tmpdir = tempfile.mkdtemp()

        # Results
        results = {}
        results['det1'] = PhotonIntensityResult()
        results['det2'] = TimeResult()
        results['det3'] = ElectronFractionResult()

        self.results = Results(results)

        self.results_zip = \
            Files.getCurrentModulePath(__file__, '../testdata/results.zip')

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testsave(self):
        zipfilepath = os.path.join(self.tmpdir, 'results.zip')
        self.results.save(zipfilepath)

        with open(zipfilepath, 'r') as fp:
            zipfile = ZipFile(fp, 'r')

            namelist = zipfile.namelist()
            self.assertTrue('keys.ini' in namelist)
            self.assertTrue('det1.csv' in namelist)
            self.assertTrue('det2.xml' in namelist)
            self.assertTrue('det3.xml' in namelist)

            zipfile.close()

    def testload(self):
        results = Results.load(self.results_zip)
        self.assertEqual(5, len(results))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

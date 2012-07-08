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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.quant.output.updater import Updater

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestUpdater(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.testdata = Files.getCurrentModulePath(__file__, '../../testdata')
        self.updater = Updater()

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testupdate_version1(self):
        src = os.path.join(self.testdata, 'old_quant_results.zip')
        dst = os.path.join(self.tmpdir, 'old_quant_results.zip')
        shutil.copy(src, dst)

        self.updater.update(dst)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

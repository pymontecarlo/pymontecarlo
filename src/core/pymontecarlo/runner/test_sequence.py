#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.runner.sequence import SequenceRunner
from pymontecarlo.runner.local import LocalRunner
from pymontecarlo.program.test_config import DummyProgram

# Globals and constants variables.

class TestSequenceRunner(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        runner = LocalRunner(DummyProgram(), self.tmpdir)

        self.runner = SequenceRunner(runner)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.runner.close()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

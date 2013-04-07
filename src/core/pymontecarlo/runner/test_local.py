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
from pymontecarlo.runner.local import LocalRunner
from pymontecarlo.program.test_config import DummyProgram

from pymontecarlo.input import Options

# Globals and constants variables.

class TestLocalRunner(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        program = DummyProgram()
        self.runner = LocalRunner(program, self.tmpdir)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testrun(self):
        self.runner.put(Options('test1'))
        self.runner.put(Options('test2'))

        self.runner.start()

        self.assertEqual(2, len(self.runner.get_results()))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

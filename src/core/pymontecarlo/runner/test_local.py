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
        self.runner.close()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testrun(self):
        # Run two options
        self.runner.start()
        self.runner.put(Options('test1'))
        self.runner.put(Options('test2'))
        self.assertEqual(2, len(self.runner.get_results()))

        # Run another options
        self.runner.put(Options('test3'))
        self.assertEqual(1, len(self.runner.get_results()))

        # Stop and restart
        self.runner.stop()
        self.runner.start()
        self.runner.put(Options('test4'))
        self.assertEqual(1, len(self.runner.get_results()))

        # Close and cannot restart
        self.runner.close()
        self.assertRaises(RuntimeError, self.runner.start)

    def testrun_exception(self):
        self.runner.start()

        self.runner.put(Options('error'))

        self.assertRaises(RuntimeError, self.runner.join)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

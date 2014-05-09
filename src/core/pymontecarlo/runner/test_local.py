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
import os

# Third party modules.

# Local modules.
from pymontecarlo.runner.local import LocalRunner
from pymontecarlo.program.test_config import DummyProgram

from pymontecarlo.options.options import Options

# Globals and constants variables.
DUMMY_PROGRAM = DummyProgram()

class TestLocalRunner(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        self.runner = LocalRunner(self.tmpdir)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.runner.close()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testrun(self):
        # Run two options
        self.runner.start()

        ops1 = Options('test1')
        ops1.programs.add(DUMMY_PROGRAM)
        self.runner.put(ops1)

        ops2 = Options('test2')
        ops2.programs.add(DUMMY_PROGRAM)
        self.runner.put(ops2)

        self.runner.join()
        self.assertEqual(2, len(os.listdir(self.tmpdir)))

        # Run another options
        ops3 = Options('test3')
        ops3.programs.add(DUMMY_PROGRAM)
        self.runner.put(ops3)

        self.runner.join()
        self.assertEqual(3, len(os.listdir(self.tmpdir)))

        # Close and cannot restart
        self.runner.close()
        self.assertRaises(RuntimeError, self.runner.start)

    def testrun_exception(self):
        self.runner.start()

        ops = Options('error')
        ops.programs.add(DUMMY_PROGRAM)
        self.runner.put(ops)

        self.assertRaises(RuntimeError, self.runner.join)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

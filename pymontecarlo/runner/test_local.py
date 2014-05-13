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

    def testrun1(self):
        ops1 = Options('test1')
        ops1.programs.add(DUMMY_PROGRAM)
        list_options = self.runner.put(ops1)
        self.assertEqual(1, len(list_options))

        ops1 = list_options[0]
        self.assertEqual(LocalRunner.STATE_QUEUED, self.runner.options_state(ops1))
        self.assertAlmostEqual(0.0, self.runner.options_progress(ops1), 4)
        self.assertEqual('queued', self.runner.options_status(ops1))

        ops2 = Options('test2')
        ops2.programs.add(DUMMY_PROGRAM)
        list_options = self.runner.put(ops2)
        self.assertEqual(1, len(list_options))

        ops2 = list_options[0]
        self.assertEqual(LocalRunner.STATE_QUEUED, self.runner.options_state(ops2))
        self.assertAlmostEqual(0.0, self.runner.options_progress(ops2), 4)
        self.assertEqual('queued', self.runner.options_status(ops2))

        self.assertAlmostEqual(0.0, self.runner.progress, 4)
        self.assertEqual('not started', self.runner.status)
        self.runner.start()

        self.runner.join()
        self.assertAlmostEqual(1.0, self.runner.progress, 4)
        self.assertEqual('running', self.runner.status)

        self.assertEqual(LocalRunner.STATE_SIMULATED, self.runner.options_state(ops1))
        self.assertAlmostEqual(1.0, self.runner.options_progress(ops1), 4)
        self.assertEqual('simulated', self.runner.options_status(ops1))

        self.assertEqual(LocalRunner.STATE_SIMULATED, self.runner.options_state(ops2))
        self.assertAlmostEqual(1.0, self.runner.options_progress(ops2), 4)
        self.assertEqual('simulated', self.runner.options_status(ops2))

        self.assertEqual(2, len(os.listdir(self.tmpdir)))

    def testrun2(self):
        ops1 = Options('test1')
        ops1.programs.add(DUMMY_PROGRAM)
        self.runner.put(ops1)

        self.runner.start()
        self.runner.join()

        ops2 = Options('test2')
        ops2.programs.add(DUMMY_PROGRAM)
        self.runner.put(ops2)

        self.runner.join()
        self.assertEqual(2, len(os.listdir(self.tmpdir)))

    def testrun3(self):
        self.runner.start()
        self.runner.close()
        self.assertRaises(RuntimeError, self.runner.start)

    def testrun4(self):
        ops = Options('error')
        ops.programs.add(DUMMY_PROGRAM)
        list_options = self.runner.put(ops)
        self.assertEqual(1, len(list_options))
        ops = list_options[0]

        self.runner.start()
        self.runner.join()

        self.assertEqual(0, len(os.listdir(self.tmpdir)))

        self.assertEqual(LocalRunner.STATE_ERROR, self.runner.options_state(ops))
        self.assertAlmostEqual(0.0, self.runner.options_progress(ops), 4)
        self.assertEqual('Options name == error', self.runner.options_status(ops))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

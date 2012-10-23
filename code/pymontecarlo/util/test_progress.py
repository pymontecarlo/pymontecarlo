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

# Third party modules.

# Local modules.
import pymontecarlo.util.progress as progress

# Globals and constants variables.

class TestProgress(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.task = progress.start_task("Task 1")

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def teststart_task(self):
        progress.stop_all()
        self.assertFalse(progress.is_running())

        progress.start_task()
        self.assertTrue(progress.is_running())

    def teststop_task(self):
        progress.stop_task(self.task)
        self.assertFalse(progress.is_running())

        progress.stop_task(self.task) # No exception

    def teststop_all(self):
        progress.stop_all()
        self.assertFalse(progress.is_running())

    def testis_running(self):
        self.assertTrue(progress.is_running())

        progress.stop_all()
        self.assertFalse(progress.is_running())

    def testprogress(self):
        self.task.progress = 0.5
        self.assertAlmostEqual(0.5, progress.progress(), 4)

        task2 = progress.start_task()
        task2.progress = 0.3
        self.assertAlmostEqual(0.4, progress.progress(), 4)

        progress.stop_all()
        self.assertAlmostEqual(0.0, progress.progress(), 4)

    def teststatus(self):
        self.task.progress = 0.8
        self.task.status = 'Abcdef'
        self.assertEqual('Abcdef', progress.status())

        task2 = progress.start_task()
        task2.progress = 0.1
        task2.status = 'xyz'
        self.assertEqual('Abcdef', progress.status())

        task2.progress = 0.9
        self.assertEqual('xyz', progress.status())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

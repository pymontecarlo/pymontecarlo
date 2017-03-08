#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.runner.local import LocalRunner

# Globals and constants variables.

class TestLocalRunner(TestCase):

    def setUp(self):
        super().setUp()

        self.r = LocalRunner(max_workers=1)

    def tearDown(self):
        super().tearDown()
        self.r.shutdown()

    def testrun1(self):
        options = self.create_basic_options()

        with self.r:
            tracker = self.r.submit(options)

        self.assertEqual(tracker.options, options)
        self.assertAlmostEqual(1.0, tracker.progress, 4)
        self.assertEqual('Done', tracker.status)
        self.assertAlmostEqual(1.0, self.r.progress, 4)
        self.assertEqual(1, self.r.options_submitted_count)
        self.assertEqual(0, self.r.options_failed_count)
        self.assertEqual(0, self.r.options_cancelled_count)
        self.assertEqual(1, self.r.options_simulated_count)

        project = self.r.project
        self.assertEqual(1, len(project.simulations))

    def testrun2(self):
        options1 = self.create_basic_options()
        options2 = self.create_basic_options()

        with self.r:
            self.r.submit(options1)
            self.r.submit(options2)

        self.assertAlmostEqual(1.0, self.r.progress, 4)
        self.assertEqual(2, self.r.options_submitted_count)
        self.assertEqual(0, self.r.options_failed_count)
        self.assertEqual(0, self.r.options_cancelled_count)
        self.assertEqual(2, self.r.options_simulated_count)

        project = self.r.project
        self.assertEqual(2, len(project.simulations))

    def testrun3(self):
        options = self.create_basic_options()

        with self.r:
            tracker = self.r.submit(options)
            tracker.cancel()

        self.assertAlmostEqual(1.0, self.r.progress, 4)
        self.assertEqual(1, self.r.options_submitted_count)
        self.assertEqual(0, self.r.options_failed_count)
        self.assertEqual(1, self.r.options_cancelled_count)
        self.assertEqual(0, self.r.options_simulated_count)

        project = self.r.project
        self.assertEqual(0, len(project.simulations))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

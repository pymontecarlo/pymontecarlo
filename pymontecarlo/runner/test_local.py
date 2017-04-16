#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.runner.local import LocalSimulationRunner

# Globals and constants variables.

class TestLocalSimulationRunner(TestCase):

    def setUp(self):
        super().setUp()

        self.r = LocalSimulationRunner(max_workers=1)

    def tearDown(self):
        super().tearDown()
        self.r.shutdown()

    def testrun1(self):
        options = self.create_basic_options()

        with self.r:
            futures = self.r.submit(options)

        self.assertEqual(1, len(futures))

        future = futures[0]
        self.assertEqual(future.result().options, options)
        self.assertAlmostEqual(1.0, future.progress, 4)
        self.assertEqual('Done', future.status)
        self.assertEqual(1, self.r.submitted_count)
        self.assertEqual(0, self.r.failed_count)
        self.assertEqual(0, self.r.cancelled_count)
        self.assertEqual(1, self.r.done_count)
        self.assertAlmostEqual(1.0, self.r.progress, 4)

        project = self.r.project
        self.assertEqual(1, len(project.simulations))

    def testrun2(self):
        options1 = self.create_basic_options()
        options2 = self.create_basic_options()

        with self.r:
            self.r.submit(options1)
            self.r.submit(options2)

        self.assertAlmostEqual(1.0, self.r.progress, 4)
        self.assertEqual(1, self.r.submitted_count)
        self.assertEqual(0, self.r.failed_count)
        self.assertEqual(0, self.r.cancelled_count)
        self.assertEqual(1, self.r.done_count)

        project = self.r.project
        self.assertEqual(1, len(project.simulations)) # Because options1 == options2

    def testrun3(self):
        options = self.create_basic_options()

        with self.r:
            futures = self.r.submit(options)
            for future in futures:
                future.cancel()

        self.assertAlmostEqual(1.0, self.r.progress, 4)
        self.assertEqual(1, self.r.submitted_count)
        self.assertEqual(0, self.r.failed_count)
        self.assertEqual(1, self.r.cancelled_count)
        self.assertEqual(0, self.r.done_count)

        project = self.r.project
        self.assertEqual(0, len(project.simulations))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

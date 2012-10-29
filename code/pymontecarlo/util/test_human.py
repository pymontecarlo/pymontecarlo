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
from pymontecarlo.util.human import human_time

# Globals and constants variables.

class TestHuman(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testhuman_time(self):
        self.assertEqual('5 sec', human_time(5))
        self.assertEqual('1 min 5 sec', human_time(65))
        self.assertEqual('1 min', human_time(60))
        self.assertEqual('1 hr 1 min 5 sec', human_time(3665))
        self.assertEqual('1 hr 1 min', human_time(3660))
        self.assertEqual('1 hr 5 sec', human_time(3605))
        self.assertEqual('1 hr', human_time(3600))
        self.assertEqual('1 day', human_time(86400))
        self.assertEqual('2 days', human_time(172800))
        self.assertEqual('1 day 1 hr', human_time(90000))
        self.assertEqual('1 day 1 hr 1 min', human_time(90060))
        self.assertEqual('1 day 1 hr 1 min 1 sec', human_time(90061))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

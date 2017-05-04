#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.human import human_time, camelcase_to_words

# Globals and constants variables.

class TestHuman(TestCase):

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

    def testcamelcase_to_words(self):
        self.assertEqual('Abc Def', camelcase_to_words('AbcDef'))
        self.assertEqual('Abc DEF', camelcase_to_words('AbcDEF'))
        self.assertEqual('Abc De F', camelcase_to_words('AbcDeF'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

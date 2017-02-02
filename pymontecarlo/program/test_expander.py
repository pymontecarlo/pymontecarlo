#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.program.expander import expand_to_single

# Globals and constants variables.

class MockA:
    pass

class MockB:
    pass

class Testexpander(TestCase):

    def testexpand_to_single(self):
        obj1 = MockA()
        obj2 = MockA()
        obj3 = MockB()
        objects = [obj1, obj2, obj3]
        combinations = expand_to_single(objects)

        self.assertEqual(2, len(combinations))

        combination = combinations[0]
        self.assertEqual(2, len(combination))
        self.assertIn(obj1, combination)
        self.assertIn(obj3, combination)

        combination = combinations[1]
        self.assertEqual(2, len(combination))
        self.assertIn(obj2, combination)
        self.assertIn(obj3, combination)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

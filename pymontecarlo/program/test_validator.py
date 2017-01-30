#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.program.validator import Validator
from pymontecarlo.options.material import Material
from pymontecarlo.exceptions import ValidationError

# Globals and constants variables.

class TestValidator(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.v = Validator()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testvalidate_material(self):
        material = Material('Pure Cu', {29: 1.0}, 8960.0)
        material2 = self.v.validate_material(material)
        self.assertEqual(material, material2)

    def testvalidate_material_exception(self):
        material = Material(' ', {120: 0.5}, -1.0)
        self.assertRaises(ValidationError, self.v.validate_material, material)

        causes = set()
        self.v._validate_material(material, causes)
        self.assertEqual(4, len(causes))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

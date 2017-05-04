#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.material import \
    MaterialSeriesHandler, VacuumSeriesHandler
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class TestMaterialSeriesHandler(TestCase):

    def testconvert(self):
        handler = MaterialSeriesHandler()
        material = Material('Brass', {29: 0.5, 30: 0.5}, 8960.0)
        s = handler.convert(material)
        self.assertEqual(3, len(s))

class TestVacuumSeriesHandler(TestCase):

    def testconvert(self):
        handler = VacuumSeriesHandler()
        material = VACUUM
        s = handler.convert(material)
        self.assertEqual(0, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

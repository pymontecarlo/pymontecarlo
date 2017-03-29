#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.fileformat.options.material import MaterialHDF5Handler
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestMaterialHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = MaterialHDF5Handler()
        material = Material('Brass', {29: 0.5, 30: 0.5}, 8960.0)
        material2 = self.convert_parse_hdf5handler(handler, material)
        self.assertEqual(material2, material)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

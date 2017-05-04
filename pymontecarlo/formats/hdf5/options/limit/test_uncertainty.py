#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.limit.uncertainty import UncertaintyLimitHDF5Handler
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class TestUncertaintyLimitHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = UncertaintyLimitHDF5Handler()
        detector = self.create_basic_photondetector()
        limit = UncertaintyLimit(XrayLine(13, 'Ka1'), detector, 0.02)
        limit2 = self.convert_parse_hdf5handler(handler, limit)
        self.assertEqual(limit2, limit)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

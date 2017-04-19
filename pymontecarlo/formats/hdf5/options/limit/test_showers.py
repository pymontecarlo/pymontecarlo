#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.limit.showers import ShowersLimitHDF5Handler
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class TestShowersLimitHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = ShowersLimitHDF5Handler()
        limit = ShowersLimit(123)
        limit2 = self.convert_parse_hdf5handler(handler, limit)
        self.assertEqual(limit2, limit)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

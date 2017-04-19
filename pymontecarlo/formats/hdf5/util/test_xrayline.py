#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.util.xrayline import XrayLineHDF5Handler
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class TestXrayLineHDF5Handler(TestCase):

    def testconvert_parse_xraytransition(self):
        handler = XrayLineHDF5Handler()
        xrayline = XrayLine(29, 'Ka1')
        xrayline2 = self.convert_parse_hdf5handler(handler, xrayline)
        self.assertEqual(xrayline2, xrayline)

    def testconvert_parse_xraytransitionset(self):
        handler = XrayLineHDF5Handler()
        xrayline = XrayLine(29, 'Ka')
        xrayline2 = self.convert_parse_hdf5handler(handler, xrayline)
        self.assertEqual(xrayline2, xrayline)

#        import h5py
#        with h5py.File('/tmp/xrayline.h5', 'w') as f:
#            handler.convert(xrayline, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

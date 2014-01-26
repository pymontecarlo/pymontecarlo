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
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.options.detector import _DelimitedDetector
from pymontecarlo.program.penepma.options.detector import index_delimited_detectors

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        det1 = _DelimitedDetector((radians(10), radians(20)), (radians(0), radians(360)))
        det2 = _DelimitedDetector((radians(20), radians(30)), (radians(0), radians(360)))
        det3 = _DelimitedDetector((radians(30), radians(40)), (radians(0), radians(360)))
        det4 = _DelimitedDetector((radians(10), radians(20)), (radians(0), radians(360)))
        det5 = _DelimitedDetector((radians(10), radians(20)), (radians(90), radians(270)))

        self.detectors = {'det1': det1, 'det2': det2, 'det3': det3,
                          'det4': det4, 'det5': det5}

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testindex_delimited_detectors(self):
        d1, d2 = index_delimited_detectors(self.detectors)
        self.assertEqual(0, d1['det1'])
        self.assertEqual(2, d1['det2'])
        self.assertEqual(3, d1['det3'])
        self.assertEqual(0, d1['det4'])
        self.assertEqual(1, d1['det5'])

        self.assertEqual(['det1', 'det4'], sorted(d2[0]))
        self.assertEqual(['det5'], d2[1])
        self.assertEqual(['det2'], d2[2])
        self.assertEqual(['det3'], d2[3])

        d1, d2 = index_delimited_detectors({})
        self.assertEqual(0, len(d1))
        self.assertEqual(0, len(d2))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

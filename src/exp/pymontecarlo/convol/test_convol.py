"""
================================================================================
:mod:`test_convol` -- Unit tests for the module MODULE.
================================================================================

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import os

# Third party modules.

# Local modules.
import DrixUtilities.Files as Files

from convol import convol

# Globals and constants variables.

class TestConvol(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        relativePath = os.path.join('..', 'testdata', 'pe-spect-01.dat')
        filepath = Files.getCurrentModulePath(__file__, relativePath)

        self.energies, self.intensities = self._read_spectrum(filepath)

    def _read_spectrum(self, filepath):
        energies = []
        intensities = []

        with open(filepath, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    break

                values = line.split()
                energies.append(float(values[0]))
                intensities.append(float(values[1]))

        return energies, intensities

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testconvol(self):
        convol(self.energies, self.intensities, 20)

#        import csv
#        writer = csv.writer(open('results.csv', 'w'))
#        for row in zip(convol_energies, convol_intensities):
#            writer.writerow(row)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

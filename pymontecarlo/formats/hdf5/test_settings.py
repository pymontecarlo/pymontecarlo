#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo import Settings
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.settings import SettingsHDF5Handler

# Globals and constants variables.

class TestSettingsHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = SettingsHDF5Handler()
        settings = Settings([self.program])
        settings2 = self.convert_parse_hdf5handler(handler, settings)
        self.assertEqual(1, len(settings2.programs))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

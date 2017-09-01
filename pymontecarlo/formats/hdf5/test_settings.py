#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.settings import SettingsHDF5Handler

# Globals and constants variables.

class TestSettingsHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = SettingsHDF5Handler()
        settings2 = self.convert_parse_hdf5handler(handler, self.settings)
        self.assertEqual(self.settings.preferred_xray_notation, settings2.preferred_xray_notation)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

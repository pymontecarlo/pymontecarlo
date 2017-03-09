#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.fileformat.settings import SettingsHDF5Handler
from pymontecarlo.settings import Settings

# Globals and constants variables.

class TestSettingsHDF5Handler(TestCase):

    def setUp(self):
        super().setUp()

        self.handler = SettingsHDF5Handler()

    def testconvert_parse(self):
        settings = Settings([self.program])

        filepath = os.path.join(self.create_temp_dir(), 'settings.h5')
        with h5py.File(filepath) as f:
            self.assertTrue(self.handler.can_convert(settings, f))
            self.handler.convert(settings, f)

        with h5py.File(filepath) as f:
            self.assertTrue(self.handler.can_parse(f))
            settings = self.handler.parse(f)

        self.assertEqual(1, len(settings.programs))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

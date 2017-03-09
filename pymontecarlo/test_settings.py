#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.settings import Settings

# Globals and constants variables.

class TestSettings(TestCase):

    def setUp(self):
        super().setUp()

        self.settings = Settings([self.program])

    def testread_write(self):
        filepath = os.path.join(self.create_temp_dir(), 'settings.h5')
        self.settings.write(filepath)

        settings = Settings.read(filepath)
        self.assertEqual(1, len(settings.programs))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

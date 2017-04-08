#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.mock import ExporterMock

# Globals and constants variables.

class TestExporter(TestCase):

    def setUp(self):
        super().setUp()

        self.e = ExporterMock()

    def testexport(self):
        options = self.create_basic_options()
        dirpath = self.create_temp_dir()
        self.e.export(options, dirpath)

        self.assertTrue(os.path.exists(os.path.join(dirpath, 'sim.json')))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

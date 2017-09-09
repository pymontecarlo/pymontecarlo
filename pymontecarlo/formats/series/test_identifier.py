#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.identifier import create_identifier, create_identifiers

# Globals and constants variables.

class Testidentifier(TestCase):

    def testcreate_identifier(self):
        options = self.create_basic_options()
        identifier = create_identifier(options)
        self.assertEqual(227, len(identifier))

    def testcreate_identifiers(self):
        options = self.create_basic_options()
        options2 = self.create_basic_options()
        options2.beam.energy_eV = 20e3
        identifiers = create_identifiers([options, options2])
        self.assertEqual(2, len(identifiers))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

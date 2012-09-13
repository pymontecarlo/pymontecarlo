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
import copy

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.particle import ELECTRON, PHOTON, POSITRON

# Globals and constants variables.

class TestParticle(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test__str__(self):
        self.assertEqual('electron', str(ELECTRON))
        self.assertEqual('photon', str(PHOTON))
        self.assertEqual('positron', str(POSITRON))

    def test__repr__(self):
        self.assertEqual('<ELECTRON>', repr(ELECTRON))
        self.assertEqual('<PHOTON>', repr(PHOTON))
        self.assertEqual('<POSITRON>', repr(POSITRON))

    def test__copy__(self):
        self.assertIs(ELECTRON, copy.copy(ELECTRON))
        self.assertIs(PHOTON, copy.copy(PHOTON))
        self.assertIs(POSITRON, copy.copy(POSITRON))

        self.assertIs(ELECTRON, copy.deepcopy(ELECTRON))
        self.assertIs(PHOTON, copy.deepcopy(PHOTON))
        self.assertIs(POSITRON, copy.deepcopy(POSITRON))

    def testcharge(self):
        self.assertEqual(-1, ELECTRON.charge)
        self.assertEqual(0, PHOTON.charge)
        self.assertEqual(1, POSITRON.charge)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

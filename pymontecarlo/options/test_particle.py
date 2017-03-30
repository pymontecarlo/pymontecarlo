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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class TestParticle(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test__str__(self):
        self.assertEqual('ELECTRON', str(Particle.ELECTRON))
        self.assertEqual('PHOTON', str(Particle.PHOTON))
        self.assertEqual('POSITRON', str(Particle.POSITRON))
#
    def testcharge(self):
        self.assertEqual(-1, Particle.ELECTRON.charge)
        self.assertEqual(0, Particle.PHOTON.charge)
        self.assertEqual(1, Particle.POSITRON.charge)

    def testcolor(self):
        self.assertEqual('#00549F', Particle.ELECTRON.color)
        self.assertEqual('#FFD700', Particle.PHOTON.color)
        self.assertEqual('#FFAB60', Particle.POSITRON.color)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

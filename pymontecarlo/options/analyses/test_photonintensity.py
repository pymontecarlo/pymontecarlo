#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.analyses.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class TestPhotonIntensityAnalysis(TestCase):

    def setUp(self):
        super().setUp()

        self.a = PhotonIntensityAnalysis()

        self.options = self._create_basic_options()

    def testapply(self):
        list_options = self.a.apply(self.options)
        self.assertEqual(0, len(list_options))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

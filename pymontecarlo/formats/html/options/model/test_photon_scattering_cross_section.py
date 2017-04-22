#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.photon_scattering_cross_section import PhotonScatteringCrossSectionModelHtmlHandler
from pymontecarlo.options.model.photon_scattering_cross_section import PhotonScatteringCrossSectionModel

# Globals and constants variables.

class TestPhotonScatteringCrossSectionModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = PhotonScatteringCrossSectionModelHtmlHandler()
        model = PhotonScatteringCrossSectionModel.BRUSA1996
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

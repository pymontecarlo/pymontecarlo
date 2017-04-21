#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.photon_scattering_cross_section import PhotonScatteringCrossSectionModelSeriesHandler
from pymontecarlo.options.model.photon_scattering_cross_section import PhotonScatteringCrossSectionModel

# Globals and constants variables.

class TestPhotonScatteringCrossSectionModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = PhotonScatteringCrossSectionModelSeriesHandler()
        model = PhotonScatteringCrossSectionModel.BRUSA1996
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

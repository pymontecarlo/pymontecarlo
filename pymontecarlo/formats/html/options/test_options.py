#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.options import OptionsHtmlHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.options.detector.photon import PhotonDetector
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)

class TestOptionsHtmlHandler(TestCase):

    def testconvert(self):
        handler = OptionsHtmlHandler()
        options = self.create_basic_options()

        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(ZINC, 20e-9)
        sample.add_layer(VACUUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        options.sample = sample

        detector = PhotonDetector('xray2', 2.2, 3.3)
        analysis = KRatioAnalysis(detector)
        analysis.add_standard_material(29, COPPER)
        analysis.add_standard_material(30, ZINC)
        options.analyses.append(analysis)

        doc = handler.convert(options)
        self.assertEqual(12, len(doc.getElementsByTagName('dt')))

#        with open('/tmp/test.html', 'w') as fp:
#            fp.write(doc.render())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

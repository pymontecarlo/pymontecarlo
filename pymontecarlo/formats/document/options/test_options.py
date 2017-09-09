#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.options import OptionsDocumentHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample
from pymontecarlo.options.material import Material
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)

class TestOptionsDocumentHandler(TestCase):

    def testconvert(self):
        handler = OptionsDocumentHandler()
        options = self.create_basic_options()

        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(ZINC, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        options.sample = sample

        photon_detector = PhotonDetector('xray2', 0.1, 0.2)
        analysis = KRatioAnalysis(photon_detector)
        options.analyses.append(analysis)

        document = self.convert_documenthandler(handler, options)
        self.assertEqual(13, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

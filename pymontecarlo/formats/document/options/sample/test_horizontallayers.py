#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.sample.horizontallayers import HorizontalLayerSampleDocumentHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)

class TestHorizontalLayerSampleDocumentHandler(TestCase):

    def testconvert(self):
        handler = HorizontalLayerSampleDocumentHandler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(ZINC, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        document = self.convert_documenthandler(handler, sample)
        self.assertEqual(7, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html5'))

    def testconvert_vacuum(self):
        handler = HorizontalLayerSampleDocumentHandler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(VACUUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        document = self.convert_documenthandler(handler, sample)
        self.assertEqual(7, self.count_document_nodes(document))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

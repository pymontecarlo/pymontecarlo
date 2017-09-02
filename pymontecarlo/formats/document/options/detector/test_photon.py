#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.detector.photon import PhotonDetectorDocumentHandler

# Globals and constants variables.

class TestPhotonDetectorDocumentHandler(TestCase):

    def testconvert(self):
        handler = PhotonDetectorDocumentHandler()
        detector = self.create_basic_photondetector()
        document = self.convert_documenthandler(handler, detector)
        self.assertEqual(8, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html5'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

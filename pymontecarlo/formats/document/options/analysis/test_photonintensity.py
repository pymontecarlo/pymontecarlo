#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.analysis.photonintensity import PhotonIntensityAnalysisDocumentHandler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class TestPhotonIntensityAnalysisDocumentHandler(TestCase):

    def testconvert(self):
        handler = PhotonIntensityAnalysisDocumentHandler()
        detector = self.create_basic_photondetector()
        analysis = PhotonIntensityAnalysis(detector)
        document = self.convert_documenthandler(handler, analysis)
        self.assertEqual(4, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

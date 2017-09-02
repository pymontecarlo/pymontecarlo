#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.beam.gaussian import GaussianBeamDocumentHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class TestGaussianBeamDocumentHandler(TestCase):

    def testconvert(self):
        handler = GaussianBeamDocumentHandler()
        beam = GaussianBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)
        document = self.convert_documenthandler(handler, beam)
        self.assertEqual(4, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

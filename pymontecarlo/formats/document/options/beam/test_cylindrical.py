#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.beam.cylindrical import CylindricalBeamDocumentHandler
from pymontecarlo.options.beam.cylindrical import CylindricalBeam
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class TestCylindricalBeamDocumentHandler(TestCase):

    def testconvert(self):
        handler = CylindricalBeamDocumentHandler()
        beam = CylindricalBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)
        document = self.convert_documenthandler(handler, beam)
        self.assertEqual(4, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

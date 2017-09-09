#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.sample.inclusion import InclusionSampleDocumentHandler
from pymontecarlo.options.sample.inclusion import InclusionSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestInclusionSampleDocumentHandler(TestCase):

    def testconvert(self):
        handler = InclusionSampleDocumentHandler()
        sample = InclusionSample(Material.pure(29), Material.pure(30), 50e-9, 0.1, 0.2)
        document = self.convert_documenthandler(handler, sample)
        self.assertEqual(7, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html5'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.material import MaterialDocumentHandler
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestMaterialDocumentHandler(TestCase):

    def testconvert(self):
        handler = MaterialDocumentHandler()
        material = Material('Brass', {29: 0.5, 30: 0.5}, 8960.0)
        document = self.convert_documenthandler(handler, material)
        self.assertEqual(10, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html5'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

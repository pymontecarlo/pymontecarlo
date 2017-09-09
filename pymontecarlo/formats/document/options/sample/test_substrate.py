#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.options.sample.substrate import SubstrateSampleDocumentHandler
from pymontecarlo.options.sample.substrate import SubstrateSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestSubstrateSampleDocumentHandler(TestCase):

    def testconvert(self):
        handler = SubstrateSampleDocumentHandler()
        sample = SubstrateSample(Material.pure(29), 0.1, 0.2)
        document = self.convert_documenthandler(handler, sample)
        self.assertEqual(5, self.count_document_nodes(document))

#        import docutils.core
#        with open('/tmp/test.html', 'wb') as fp:
#            fp.write(docutils.core.publish_from_doctree(document, writer_name='html5'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

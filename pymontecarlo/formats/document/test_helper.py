#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.document.helper import publish_html
from pymontecarlo.formats.document.options.options import OptionsDocumentHandler
from pymontecarlo.formats.document.builder import DocumentBuilder

# Globals and constants variables.

class Testhelper(TestCase):

    def testpublish_html(self):
        handler = OptionsDocumentHandler()
        options = self.create_basic_options()
        builder = DocumentBuilder(self.settings)
        handler.convert(options, builder)

        s = publish_html(builder)
        self.assertEqual(16689, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

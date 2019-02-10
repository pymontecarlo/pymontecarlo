#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.helper import publish_html, count_document_nodes
from pymontecarlo.formats.document.options.options import OptionsDocumentHandler
from pymontecarlo.formats.document.builder import DocumentBuilder

# Globals and constants variables.

def test_publish_html(options, settings):
    handler = OptionsDocumentHandler()
    builder = DocumentBuilder(settings)
    handler.convert(options, builder)

    s = publish_html(builder)
    assert len(s) == 16708

def test_count_document_nodes(options, settings):
    handler = OptionsDocumentHandler()
    builder = DocumentBuilder(settings)
    handler.convert(options, builder)

    document = builder.build()

    assert count_document_nodes(document) == 14

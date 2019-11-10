#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document import publish_html

# Globals and constants variables.


def test_publish_html(options, documentbuilder):
    options.convert_document(documentbuilder)

    s = publish_html(documentbuilder)
    assert len(s) > 0

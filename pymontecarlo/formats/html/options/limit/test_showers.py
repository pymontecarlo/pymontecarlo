#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.limit.showers import ShowersLimitHtmlHandler
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class TestShowersLimitHtmlHandler(TestCase):

    def testconvert(self):
        handler = ShowersLimitHtmlHandler()
        limit = ShowersLimit(123)
        root = handler.convert(limit)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

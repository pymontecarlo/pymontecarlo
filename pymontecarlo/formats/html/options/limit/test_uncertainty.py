#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.limit.uncertainty import UncertaintyLimitHtmlHandler
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class TestUncertaintyLimitHtmlHandler(TestCase):

    def testconvert(self):
        handler = UncertaintyLimitHtmlHandler()
        detector = self.create_basic_photondetector()
        limit = UncertaintyLimit(XrayLine(13, 'Ka1'), detector, 0.02)
        root = handler.convert(limit)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

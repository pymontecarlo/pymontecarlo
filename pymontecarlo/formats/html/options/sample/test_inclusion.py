#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.sample.inclusion import InclusionSampleHtmlHandler
from pymontecarlo.options.sample.inclusion import InclusionSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestInclusionSampleHtmlHandler(TestCase):

    def testconvert(self):
        handler = InclusionSampleHtmlHandler()
        sample = InclusionSample(Material.pure(29), Material.pure(30), 50e-9, 0.1, 0.2)
        root = handler.convert(sample)
        self.assertEqual(8, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

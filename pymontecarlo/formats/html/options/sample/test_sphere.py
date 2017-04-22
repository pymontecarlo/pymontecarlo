#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.sample.sphere import SphereSampleHtmlHandler
from pymontecarlo.options.sample.sphere import SphereSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestSphereSampleHtmlHandler(TestCase):

    def testconvert(self):
        handler = SphereSampleHtmlHandler()
        sample = SphereSample(Material.pure(29), 50e-9, 0.1, 0.2)
        root = handler.convert(sample)
        self.assertEqual(6, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

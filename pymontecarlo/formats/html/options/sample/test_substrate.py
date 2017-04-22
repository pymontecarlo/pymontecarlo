#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.sample.substrate import SubstrateSampleHtmlHandler
from pymontecarlo.options.sample.substrate import SubstrateSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestSubstrateSampleHtmlHandler(TestCase):

    def testconvert(self):
        handler = SubstrateSampleHtmlHandler()
        sample = SubstrateSample(Material.pure(29), 0.1, 0.2)
        root = handler.convert(sample)
        self.assertEqual(4, len(root.children))

#        with open('/tmp/test.html', 'w') as fp:
#            fp.write(root.render())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

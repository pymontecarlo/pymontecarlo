#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.material import MaterialHtmlHandler
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestMaterialHtmlHandler(TestCase):

    def testconvert(self):
        handler = MaterialHtmlHandler()
        material = Material('Brass', {29: 0.5, 30: 0.5}, 8960.0)
        root = handler.convert(material)
        self.assertEqual(1, len(root.children))

#        with open('/tmp/test.html', 'w') as fp:
#            fp.write(root.render())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

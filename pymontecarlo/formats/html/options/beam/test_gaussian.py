#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.beam.gaussian import GaussianBeamHtmlHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class TestGaussianBeamHtmlHandler(TestCase):

    def testconvert(self):
        handler = GaussianBeamHtmlHandler()
        beam = GaussianBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)
        root = handler.convert(beam)
        self.assertEqual(1, len(root.children))

#        with open('/tmp/test.html', 'w') as fp:
#            fp.write(root.render())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.mock import ProgramHtmlHandlerMock

# Globals and constants variables.

class TestProgramHtmlHandler(TestCase):

    def testconvert(self):
        handler = ProgramHtmlHandlerMock()
        options = self.create_basic_program()
        s = handler.convert(options, self.settings)
        self.assertEqual(2, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

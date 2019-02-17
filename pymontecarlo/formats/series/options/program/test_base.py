#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.mock import ProgramSeriesHandlerMock

# Globals and constants variables.

class TestProgramSeriesHandler(TestCase):

    def testconvert(self):
        handler = ProgramSeriesHandlerMock()
        program = self.create_basic_program()
        s = self.convert_serieshandler(handler, program)
        self.assertEqual(3, len(s))
        self.assertEqual('mock', s['program'])
        self.assertEqual(100, s['number trajectories'])
        self.assertEqual('MOTT_CZYZEWSKI1990', s['elastic cross section model'])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

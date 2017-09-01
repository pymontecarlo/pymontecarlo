#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.mock import ProgramHDF5HandlerMock

# Globals and constants variables.

class TestProgramHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = ProgramHDF5HandlerMock()
        program = self.create_basic_program()
        program2 = self.convert_parse_hdf5handler(handler, program)
#        print(options.program, options2.program, options.program == options2.program)
#        print(options.beam, options2.beam, options.beam == options2.beam)
#        print(options.sample, options2.sample, options.sample == options2.sample)
#        print(options.analyses, options2.analyses)
#        print(options.limits, options2.limits)
#        print(options.models, options2.models)
        self.assertEqual(program2, program)

#        import h5py
#        with h5py.File('/tmp/options.h5', 'w')

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

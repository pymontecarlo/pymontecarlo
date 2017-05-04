#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.options import OptionsHDF5Handler

# Globals and constants variables.

class TestOptionsHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = OptionsHDF5Handler()
        options = self.create_basic_options()
        options2 = self.convert_parse_hdf5handler(handler, options)
#        print(options.program, options2.program, options.program == options2.program)
#        print(options.beam, options2.beam, options.beam == options2.beam)
#        print(options.sample, options2.sample, options.sample == options2.sample)
#        print(options.analyses, options2.analyses)
#        print(options.limits, options2.limits)
#        print(options.models, options2.models)
        self.assertEqual(options2, options)

#        import h5py
#        with h5py.File('/tmp/options.h5', 'w') as f:
#            handler.convert(options, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

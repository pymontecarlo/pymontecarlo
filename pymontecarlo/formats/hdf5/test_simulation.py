#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.simulation import SimulationHDF5Handler

# Globals and constants variables.

class TestSimulationHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = SimulationHDF5Handler()
        sim = self.create_basic_simulation()
        sim2 = self.convert_parse_hdf5handler(handler, sim)
        self.assertEqual(sim2, sim)

#        import h5py
#        with h5py.File('/tmp/sim.h5', 'w') as f:
#            handler.convert(sim, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

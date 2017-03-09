#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os

# Third party modules.
import h5py
import numpy as np

# Local modules.
from pymontecarlo.testcase import TestCase
import pymontecarlo.util.hdf5util as hdf5util

# Globals and constants variables.

class TestModule(TestCase):

    def setUp(self):
        super().setUp()

        self.tmpdir = self.create_temp_dir()

        # Create test HDF5
        self.original = h5py.File(os.path.join(self.tmpdir, 'original.h5'), 'w')
        self.original.attrs['a'] = 1
        g1 = self.original.create_group('group1')
        g1.attrs['b'] = 2
        g1.create_dataset('data1', data=np.ones((2, 2)))

    def testhdf5util(self):
        copy = h5py.File(os.path.join(self.tmpdir, 'copy.h5'), 'w')
        hdf5util.copy(self.original, copy)

        self.assertEqual(1, copy.attrs['a'])
        self.assertEqual(2, copy['group1'].attrs['b'])
        self.assertEqual(4, np.sum(copy['group1']['data1']))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

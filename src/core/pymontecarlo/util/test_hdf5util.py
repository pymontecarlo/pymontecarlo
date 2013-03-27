#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import tempfile
import shutil
import os

# Third party modules.
import h5py
import numpy as np

# Local modules.
import pymontecarlo.util.hdf5util as hdf5util

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        # Create test HDF5
        self.original = h5py.File(os.path.join(self.tmpdir, 'original.h5'), 'w')
        self.original.attrs['a'] = 1
        g1 = self.original.create_group('group1')
        g1.attrs['b'] = 2
        g1.create_dataset('data1', data=np.ones((2, 2)))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testhdf5util(self):
        copy = h5py.File(os.path.join(self.tmpdir, 'copy.h5'), 'w')
        hdf5util.copy(self.original, copy)

        self.assertEqual(1, copy.attrs['a'])
        self.assertEqual(2, copy['group1'].attrs['b'])
        self.assertEqual(4, np.sum(copy['group1']['data1']))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

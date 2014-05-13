#!/usr/bin/env python
"""
================================================================================
:mod:`hdf5util` -- Utilities for HDF5
================================================================================

.. module:: hdf5util
   :synopsis: Utilities for HDF5

.. inheritance-diagram:: pymontecarlo.util.hdf5util

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import h5py

# Local modules.

# Globals and constants variables.

def copy_attrs(src, dest):
    """
    Copies attributes from source to destination.
    """
    for key, value in src.attrs.items():
        dest.attrs[key] = value

def copy(src, dest):
    """
    Copies groups, datasets and attributes from source to destination
    """
    def c(key, value):
        if isinstance(value, h5py.Group):
            dest.create_group(key)
            copy_attrs(value, dest[key])
        elif isinstance(value, h5py.Dataset):
            dest.create_dataset(key, data=value)
            copy_attrs(value, dest[key])

    src.visititems(c)
    copy_attrs(src, dest)

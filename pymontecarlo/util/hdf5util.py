"""
Utilities for HDF5
"""

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

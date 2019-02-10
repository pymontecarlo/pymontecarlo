""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.

# Globals and constants variables.

def convert_parse_hdf5handler(handler, obj, tmp_path):
    filepath = tmp_path.joinpath('object.h5')

    with h5py.File(filepath) as f:
        assert handler.can_convert(obj, f)
        handler.convert(obj, f)

    with h5py.File(filepath) as f:
        assert handler.can_parse(f)
        obj2 = handler.parse(f)

    return obj2
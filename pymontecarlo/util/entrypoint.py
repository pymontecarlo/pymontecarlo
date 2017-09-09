""""""

# Standard library modules.
import threading

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.

# Globals and constants variables.
_ENTRYPOINTS = {}

ENTRYPOINT_PROGRAMS = 'pymontecarlo.program'
ENTRYPOINT_HDF5HANDLER = 'pymontecarlo.formats.hdf5'
ENTRYPOINT_DOCUMENTHANDLER = 'pymontecarlo.formats.document'
ENTRYPOINT_SERIESHANDLER = 'pymontecarlo.formats.series'

def resolve_entrypoints(group):
    """
    Returns a dictionary where the keys are the entry point's name and
    the values are the entry point.
    """
    if group in _ENTRYPOINTS:
        return _ENTRYPOINTS[group]

    # NOTE: This is an important check. If the entry points are resolved in
    # another thread than the main one, the import hangs
    if threading.current_thread() != threading.main_thread():
        raise RuntimeError('Handler must be initialized in main thread')

    entrypoints = dict((ep.name, ep) for ep in iter_entry_points(group))
    _ENTRYPOINTS[group] = entrypoints
    return entrypoints

def reset_entrypoints():
    _ENTRYPOINTS.clear()
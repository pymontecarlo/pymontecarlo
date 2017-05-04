""""""

# Standard library modules.
import threading

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.

# Globals and constants variables.
_ENTRYPOINTS = {}

def resolve_entrypoints(group):
    """
    Returns a dictionary where the keys are the entry point's name and
    the values are the entry point's class.
    """
    if group in _ENTRYPOINTS:
        return _ENTRYPOINTS[group]

    # NOTE: This is an important check. If the entry points are resolved in
    # another thread than the main one, the import hangs
    if threading.current_thread() != threading.main_thread():
        raise RuntimeError('Handler must be initialized in main thread')

    entrypoints = tuple(ep.resolve() for ep in iter_entry_points(group))
    _ENTRYPOINTS[group] = entrypoints
    return entrypoints

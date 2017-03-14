""""""

# Standard library modules.
import threading

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.

# Globals and constants variables.

def resolve_entrypoints(group):
    """
    Returns a dictionary where the keys are the entry point's name and
    the values are the entry point's class.
    """
    # NOTE: This is an important check. If the entry points are resolved in
    # another thread than the main one, the import hangs
    if threading.current_thread() != threading.main_thread():
        raise RuntimeError('Handler must be initialized in main thread')

    return tuple(ep.resolve() for ep in iter_entry_points(group))
""""""

# Standard library modules.
import weakref

# Third party modules.

# Local modules.

# Globals and constants variables.

class _BoundSignal:

    def __init__(self):
        self._handlers = []

    def _iter_handlers(self):
        for ref in list(self._handlers):
            func = ref()
            if func is None:
                self._handlers.remove(ref)
                continue
            yield ref, func

    def connect(self, func):
        self._handlers.append(weakref.WeakMethod(func))

    def disconnect(self, func):
        for ref, other_func in self._iter_handlers():
            if func == other_func:
                self._handlers.remove(ref)

    def send(self, *args, **kwargs):
        for _ref, func in self._iter_handlers():
            func(*args, **kwargs)

class Signal:

    def __init__(self):
        self._bounds = weakref.WeakKeyDictionary()

    def __get__(self, obj, type=None):
        if obj not in self._bounds:
            self._bounds[obj] = _BoundSignal()
        return self._bounds[obj]

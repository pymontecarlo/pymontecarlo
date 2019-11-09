""""""

# Standard library modules.
import warnings as warnings_module
import asyncio

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import AccumulatedWarning, AccumulatedError

# Globals and constants variables.


class ErrorAccumulator:
    def __init__(self, warning_class=None, exception_class=None):
        if warning_class is None:
            warning_class = AccumulatedWarning
        self._warning_class = warning_class

        if exception_class is None:
            exception_class = AccumulatedError
        self._exception_class = exception_class

        self._exceptions = set()
        self._warnings = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is asyncio.CancelledError:
            raise

        if exc_type is not None:
            self.add_exception(exc_type(exc_value))

        if self._warnings:
            warning = self._warning_class(*self._warnings)
            warnings_module.warn(warning)

        if self._exceptions:
            raise self._exception_class(*self._exceptions)

    def add_exception(self, exception):
        self._exceptions.add(exception)

    def add_warning(self, warning):
        self._warnings.add(warning)

    def clear(self):
        self._exceptions.clear()
        self._warnings.clear()

    @property
    def exceptions(self):
        return frozenset(self._exceptions)

    @property
    def warnings(self):
        return frozenset(self._warnings)

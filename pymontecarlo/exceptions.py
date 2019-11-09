"""
Exceptions of pymontecarlo.
"""

# Note:
# As suggested by https://julien.danjou.info/blog/2016/python-exceptions-guide,
# it is recommended to group all exceptions of a library inside a single module.

# Standard library modules.
import textwrap

# Third party modules.

# Local modules.

# Globals and constants variables.


class AccumulatedMixin:

    _textwrapper = textwrap.TextWrapper(
        initial_indent="  - ", subsequent_indent=" " * 4
    )

    def __init__(self, *causes):
        message = "The following causes were given:\n"
        message += "\n".join(
            "\n".join(self._textwrapper.wrap(str(cause))) for cause in causes
        )
        super().__init__(message)
        self.causes = tuple(causes)


class PymontecarloError(Exception):
    """Base exception of pymontecarlo."""


class PymontecarloWarning(Warning):
    pass


class AccumulatedError(PymontecarloError, AccumulatedMixin):
    pass


class AccumulatedWarning(PymontecarloWarning, AccumulatedMixin):
    pass


class ValidationError(AccumulatedError):
    """Exception raised by validators"""


class ValidationWarning(AccumulatedWarning):
    """Warning raised by validators"""


class ExportError(AccumulatedError):
    pass


class ExportWarning(AccumulatedWarning):
    pass


class WorkerError(PymontecarloError):
    pass


class ImportError(AccumulatedError):
    pass


class ImportWarning(AccumulatedWarning):
    pass


class ProgramNotFound(PymontecarloError):
    pass


class ProgramNotLoadedWarning(PymontecarloWarning):
    pass


class ParseError(PymontecarloError):
    pass


class ConvertError(PymontecarloError):
    pass

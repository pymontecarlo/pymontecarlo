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

class PymontecarloError(Exception):
    """Base exception of pymontecarlo."""

class AccumulatedError(PymontecarloError):

    _textwrapper = textwrap.TextWrapper(initial_indent='  - ',
                                        subsequent_indent=' ' * 4)

    def __init__(self, *causes):
        message = 'Validation failed for the following reasons:\n'
        message += '\n'.join('\n'.join(self._textwrapper.wrap(str(cause)))
                             for cause in causes)
        super().__init__(message)
        self.causes = tuple(causes)

class ValidationError(AccumulatedError):
    """Exception raised by validators"""

class ExportError(AccumulatedError):
    pass

class WorkerError(PymontecarloError):
    pass

class WorkerCancelledError(PymontecarloError):
    pass

class ImportError_(AccumulatedError):
    pass

class ProgramNotFound(PymontecarloError):
    pass

class ParseError(PymontecarloError):
    pass

class ConvertError(PymontecarloError):
    pass

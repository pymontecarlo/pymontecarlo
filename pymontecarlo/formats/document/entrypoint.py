""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import ConvertError
from pymontecarlo.util.entrypoint import resolve_entrypoints, ENTRYPOINT_DOCUMENTHANDLER

# Globals and constants variables.

def find_convert_documenthandler(obj):
    for entrypoint in resolve_entrypoints(ENTRYPOINT_DOCUMENTHANDLER).values():
        clasz = entrypoint.resolve()
        handler = clasz()
        if handler.can_convert(obj):
            return handler
    raise ConvertError("No handler found for object {!r}".format(obj))
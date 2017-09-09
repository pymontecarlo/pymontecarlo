""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import ParseError, ConvertError
from pymontecarlo.util.entrypoint import resolve_entrypoints, ENTRYPOINT_HDF5HANDLER

# Globals and constants variables.

def find_parse_hdf5handler(group):
    for entrypoint in resolve_entrypoints(ENTRYPOINT_HDF5HANDLER).values():
        clasz = entrypoint.resolve()
        handler = clasz()
        if handler.can_parse(group):
            return handler
    raise ParseError("No handler found for group: {!r}".format(group))

def find_convert_hdf5handler(obj, group):
    for entrypoint in resolve_entrypoints(ENTRYPOINT_HDF5HANDLER).values():
        clasz = entrypoint.resolve()
        handler = clasz()
        if handler.can_convert(obj, group):
            return handler
    raise ConvertError("No handler found for object {!r} and group {!r}"
                       .format(obj, group))

""""""

# Standard library modules.
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.util.entrypoint import \
    resolve_entrypoints, ENTRYPOINT_PROGRAMS
from pymontecarlo.exceptions import ProgramNotFound, ProgramNotLoadedWarning

# Globals and constants variables.

def is_available(name):
    return name in resolve_entrypoints(ENTRYPOINT_PROGRAMS)

def resolve(name):
    """
    Returns an instance of a program.
    
    :exc: raises :class:`ProgramNotFound` if no program is found
    """
    try:
        entrypoint = resolve_entrypoints(ENTRYPOINT_PROGRAMS)[name]
    except KeyError:
        raise ProgramNotFound('Program {} does not exist'.format(name))

    clasz = entrypoint.resolve()
    return clasz()

def resolve_all():
    programs = []

    for name, entrypoint in resolve_entrypoints(ENTRYPOINT_PROGRAMS).items():
        try:
            clasz = entrypoint.resolve()
        except Exception as ex:
            message = "Error resolving {}: {}".format(name, str(ex))
            warnings.warn(message, ProgramNotLoadedWarning)
            continue

        try:
            program = clasz()
        except Exception as ex:
            message = "Error initializing {}: {}".format(name, str(ex))
            warnings.warn(message, ProgramNotLoadedWarning)
            continue

        programs.append(program)

    return tuple(programs)

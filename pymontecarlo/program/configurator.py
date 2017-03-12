""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Configurator:

    @abc.abstractmethod
    def prepare_parser(self, parser, program=None):
        raise NotImplementedError

    @abc.abstractmethod
    def create_program(self, namespace, clasz):
        raise NotImplementedError

    @abc.abstractproperty
    def fullname(self):
        raise NotImplementedError

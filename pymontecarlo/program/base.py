"""
Base program
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Program(metaclass=abc.ABCMeta):

    def __repr__(self):
        return '<{classname}({name})>' \
            .format(classname=self.__class__.__name__, name=self.name)

    @abc.abstractmethod
    def create_expander(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_validator(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_exporter(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_worker(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_importer(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_default_limits(self, options):
        raise NotImplementedError

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError

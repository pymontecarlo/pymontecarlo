"""
Base program
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.options.base import Option

# Globals and constants variables.

class Program(Option, metaclass=abc.ABCMeta):

    def __repr__(self):
        return '<{classname}({name})>' \
            .format(classname=self.__class__.__name__, name=self.getidentifier())

    @abc.abstractclassmethod
    def getidentifier(cls): #@NoSelf
        """
        Returns key to identify program. Should not contain any white space.
        
        .. note:: This is a class method.
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def create_configurator(cls): #@NoSelf
        """
        .. note:: This is a class method.
        """
        raise NotImplementedError

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

    def create_datarow(self, **kwargs):
        #TODO: Implement datarow
        return super().create_datarow(**kwargs)

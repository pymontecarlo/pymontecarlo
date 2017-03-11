"""
Base program
"""

# Standard library modules.
import abc
import argparse

# Third party modules.

# Local modules.

# Globals and constants variables.

class Program(metaclass=abc.ABCMeta):

    @abc.abstractstaticmethod
    def getfullname(): #@NoSelf
        raise NotImplementedError

    @abc.abstractstaticmethod
    def getname(): #@NoSelf
        raise NotImplementedError

    @abc.abstractclassmethod
    def prepare_parser(cls, parser): #@NoSelf
        raise NotImplementedError

    @abc.abstractclassmethod
    def from_namespace(cls, ns): #@NoSelf
        raise NotImplementedError

    def __repr__(self):
        return '<{classname}({name})>' \
            .format(classname=self.__class__.__name__, name=self.getfullname())

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
    def namespace(self):
        return argparse.Namespace()

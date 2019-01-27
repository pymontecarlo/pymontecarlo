"""
Base program
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.options.base import OptionBase, OptionBuilderBase

# Globals and constants variables.

class ProgramBase(OptionBase):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<{classname}({name})>' \
            .format(classname=self.__class__.__name__, name=self.name)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.name == other.name

    @abc.abstractmethod
    def create_expander(self):
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

class ProgramBuilderBase(OptionBuilderBase):
    pass

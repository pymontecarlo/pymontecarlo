"""
Base models.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.options.option import Option

# Globals and constants variables.

class Model(Option):

    def __init__(self, name, reference=''):
        self.name = name
        self.reference = reference

    def __repr__(self):
        return '<{classname}({name})>' \
            .format(classname=self.__class__.__name__,
                    name=self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.name == other.name and \
            self.reference == other.reference

    @abc.abstractproperty
    def category(self):
        raise NotImplementedError

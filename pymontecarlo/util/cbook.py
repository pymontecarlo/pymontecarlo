""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Builder(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def build(self):
        raise NotImplementedError

class MultiplierAttribute(object):

    def __init__(self, attrname, multiplier):
        self.attrname = attrname
        self.multiplier = multiplier

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.attrname) * self.multiplier

    def __set__(self, instance, value):
        setattr(instance, self.attrname, value / self.multiplier)

    def __delete__(self, instance):
        delattr(instance, self.attrname)

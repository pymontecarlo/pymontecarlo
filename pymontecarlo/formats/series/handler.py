""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class SeriesHandlerBase(metaclass=abc.ABCMeta):

    def can_convert(self, obj):
        return type(obj) is self.CLASS

    @abc.abstractmethod
    def convert(self, obj, builder):
        pass

    @abc.abstractproperty
    def CLASS(self):
        raise NotImplementedError

    @property
    def VERSION(self):
        return 1

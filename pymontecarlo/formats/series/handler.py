""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.builder import SeriesBuilder

# Globals and constants variables.

class SeriesHandler(object, metaclass=abc.ABCMeta):

    def __init__(self, settings):
        self.settings = settings

    def can_convert(self, obj):
        return type(obj) is self.CLASS

    def convert(self, obj, abbreviate_name=False, format_number=False, return_tolerances=False):
        return self._convert(obj).build(abbreviate_name, format_number, return_tolerances)

    @abc.abstractmethod
    def _convert(self, obj):
        return SeriesBuilder(self.settings)

    @abc.abstractproperty
    def CLASS(self):
        raise NotImplementedError

    @property
    def VERSION(self):
        return 1

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

    def convert(self, obj, abbreviate_name=False, format_number=False):
        builder = self.create_builder(obj)
        builder.abbreviate_name = abbreviate_name
        builder.format_number = format_number
        return builder.build()

    @abc.abstractmethod
    def create_builder(self, obj):
        return SeriesBuilder(self.settings)

    @abc.abstractproperty
    def CLASS(self):
        raise NotImplementedError

    @property
    def VERSION(self):
        return 1

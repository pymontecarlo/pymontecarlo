""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler

# Globals and constants variables.

class ModelHDF5Handler(HDF5Handler):

    ATTR_NAME = 'name'

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_NAME in group.attrs

    def parse(self, group):
        name = group.attrs[self.ATTR_NAME]
        return self.CLASS.__members__[name]

    def convert(self, model, group):
        super().convert(model, group)
        group.attrs[self.ATTR_NAME] = model.name

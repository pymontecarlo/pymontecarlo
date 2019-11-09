"""
Base detector.
"""

# Standard library modules.

# Third party modules.

# Local modules.
import pymontecarlo.options.base as base

# Globals and constants variables.


class DetectorBase(base.OptionBase):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __eq__(self, other):
        return super().__eq__(other) and base.isclose(self.name, other.name)

    # region HDF5

    ATTR_NAME = "name"

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_NAME, self.name)


# endregion


class DetectorBuilderBase(base.OptionBuilderBase):
    pass

"""
Simulation.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.entity import EntityBase, EntityHDF5Mixin
from pymontecarlo.util.cbook import find_by_type
from pymontecarlo.formats.identifier import create_identifier

# Globals and constants variables.


class Simulation(EntityBase, EntityHDF5Mixin):
    def __init__(self, options, results=None, identifier=None):
        self.options = options

        if results is None:
            results = []
        self.results = results.copy()

        if identifier is None:
            identifier = create_identifier(options)
        self.identifier = identifier

    def __eq__(self, other):
        # NOTE: This is on design since two simulations should have the
        # same or equivalent results if their options are the same
        return self.options == other.options

    def find_result(self, result_class):
        return find_by_type(self.results, result_class)

    # region HDF5

    ATTR_IDENTIFIER = "identifier"
    GROUP_OPTIONS = "options"
    GROUP_RESULTS = "results"

    @classmethod
    def parse_hdf5(cls, group):
        options = cls._parse_hdf5_object(group[cls.GROUP_OPTIONS])
        results = [
            cls._parse_hdf5_object(group_result)
            for group_result in group[cls.GROUP_RESULTS].values()
        ]
        identifier = cls._parse_hdf5(group, cls.ATTR_IDENTIFIER, str)
        return cls(options, results, identifier)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_IDENTIFIER, self.identifier)

        group_options = group.create_group(self.GROUP_OPTIONS)
        self.options.convert_hdf5(group_options)

        group_results = group.create_group(self.GROUP_RESULTS)
        for result in self.results:
            name = "{} [{:d}]".format(result.__class__.__name__, id(result))
            group_result = group_results.create_group(name)
            result.convert_hdf5(group_result)


# endregion

""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.simulation import Simulation

# Globals and constants variables.

class SimulationHDF5Handler(HDF5Handler):

    ATTR_IDENTIFIER = 'identifier'
    GROUP_OPTIONS = 'options'
    GROUP_RESULTS = 'results'

    def _parse_options(self, group):
        group_options = group[self.GROUP_OPTIONS]
        return self._parse_hdf5handlers(group_options)

    def _parse_results(self, group):
        group_results = group[self.GROUP_RESULTS]

        results = []
        for group_result in group_results.values():
            result = self._parse_hdf5handlers(group_result)
            results.append(result)

        return results

    def _parse_identifier(self, group):
        return group.attrs[self.ATTR_IDENTIFIER]

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.GROUP_OPTIONS in group and \
            self.GROUP_RESULTS in group and \
            self.ATTR_IDENTIFIER in group.attrs

    def parse(self, group):
        options = self._parse_options(group)
        results = self._parse_results(group)
        identifier = self._parse_identifier(group)
        return self.CLASS(options, results, identifier)

    def _convert_options(self, options, group):
        group_options = group.create_group(self.GROUP_OPTIONS)
        self._convert_hdf5handlers(options, group_options)

    def _convert_results(self, results, group):
        group_results = group.create_group(self.GROUP_RESULTS)

        for result in results:
            name = '{} [{:d}]'.format(result.__class__.__name__, id(result))
            group_result = group_results.create_group(name)
            self._convert_hdf5handlers(result, group_result)

    def _convert_identifier(self, identifier, group):
        group.attrs[self.ATTR_IDENTIFIER] = identifier

    def convert(self, simulation, group):
        super().convert(simulation, group)
        self._convert_options(simulation.options, group)
        self._convert_results(simulation.results, group)
        self._convert_identifier(simulation.identifier, group)

    @property
    def CLASS(self):
        return Simulation

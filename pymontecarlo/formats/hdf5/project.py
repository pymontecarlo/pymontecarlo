""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.project import Project

# Globals and constants variables.

class ProjectHDF5Handler(HDF5Handler):

    GROUP_SIMULATIONS = 'simulations'

    def _parse_simulations(self, group):
        group_simulations = group[self.GROUP_SIMULATIONS]

        simulations = []
        for group_simulation in group_simulations.values():
            simulation = self._parse_hdf5handlers(group_simulation)
            simulations.append(simulation)

        return simulations

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.GROUP_SIMULATIONS in group

    def parse(self, group):
        filepath = group.file.filename
        project = self.CLASS(filepath)
        project.simulations += self._parse_simulations(group)
        return project

    def _convert_simulations(self, simulations, group):
        group_simulations = group.create_group(self.GROUP_SIMULATIONS)

        for simulation in simulations:
            name = simulation.identifier
            group_simulation = group_simulations.create_group(name)
            self._convert_hdf5handlers(simulation, group_simulation)

    def convert(self, project, group):
        super().convert(project, group)
        self._convert_simulations(project.simulations, group)

    @property
    def CLASS(self):
        return Project


""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import ParseError
from pymontecarlo.fileformat.base import HDF5Handler
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class BeamHDF5Handler(HDF5Handler):

    ATTR_ENERGY = 'energy_eV'
    ATTR_PARTICLE = 'particle'

    def _parse_energy_eV(self, group):
        return float(group.attrs[self.ATTR_ENERGY])

    def _parse_particle(self, group):
        name = group.attrs[self.ATTR_PARTICLE]
        if name not in Particle.__members__:
            raise ParseError('No particle matching "{}"'.format(name))
        return Particle.__members__[name]

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_ENERGY in group.attrs and \
            self.ATTR_PARTICLE in group.attrs

    def _convert_energy_eV(self, beam, group):
        group.attrs[self.ATTR_ENERGY] = beam.energy_eV

    def _convert_particle(self, beam, group):
        group.attrs[self.ATTR_PARTICLE] = beam.particle.name

    @abc.abstractmethod
    def convert(self, beam, group):
        super().convert(beam, group)
        self._convert_energy_eV(beam, group)
        self._convert_particle(beam, group)

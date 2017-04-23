""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import ParseError
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class BeamHDF5HandlerMixin:

    GROUP_BEAMS = 'beams'

    def _parse_beam_internal(self, group, ref_beam):
        group_beam = group.file[ref_beam]
        return self._parse_hdf5handlers(group_beam)

    def _require_beams_group(self, group):
        return group.file.require_group(self.GROUP_BEAMS)

    def _convert_beam_internal(self, beam, group):
        group_beams = self._require_beams_group(group)

        name = '{} [{:d}]'.format(beam.__class__.__name__, id(beam))
        if name in group_beams:
            return group_beams[name]

        group_beam = group_beams.create_group(name)

        self._convert_hdf5handlers(beam, group_beam)

        return group_beam

class BeamHDF5Handler(HDF5Handler):

    ATTR_ENERGY = 'energy (eV)'
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

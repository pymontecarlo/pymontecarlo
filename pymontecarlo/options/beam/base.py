"""
Base classes for beams.
"""

# Standard library modules.
import functools
import operator

# Third party modules.

# Local modules.
import pymontecarlo.options.base as base
from pymontecarlo.options.particle import Particle
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.


class BeamBase(base.OptionBase):
    """
    Base beam.
    """

    ENERGY_TOLERANCE_eV = 1e-2  # 0.01 eV

    def __init__(self, energy_eV, particle=Particle.ELECTRON):
        """
        :arg energy_eV: initial energy of the particle(s)
        :type energy_eV: :class:`float`
        
        :arg particle: type of particles [default: :data:`.ELECTRON`]
        :type particle: :mod:`.particle`
        """
        super().__init__()

        self.energy_eV = energy_eV
        self.particle = particle

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(
                self.energy_eV, other.energy_eV, abs_tol=self.ENERGY_TOLERANCE_eV
            )
            and base.isclose(self.particle, other.particle)
        )

    energy_keV = base.MultiplierAttribute("energy_eV", 1e-3)

    # region HDF5

    ATTR_ENERGY = "energy (eV)"
    ATTR_PARTICLE = "particle"

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_ENERGY, self.energy_eV)
        self._convert_hdf5(group, self.ATTR_PARTICLE, self.particle)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_column(
            "beam energy", "E0", self.energy_eV, "eV", self.ENERGY_TOLERANCE_eV
        )
        builder.add_column("beam particle", "par", str(self.particle))

    # endregion

    # region Document

    DESCRIPTION_BEAM = "beam"

    def convert_document(self, builder):
        super().convert_document(builder)

        builder.add_title(camelcase_to_words(self.__class__.__name__))

        description = builder.require_description(self.DESCRIPTION_BEAM)
        description.add_item("Energy", self.energy_eV, "eV", self.ENERGY_TOLERANCE_eV)
        description.add_item("Particle", self.particle)


# endregion


class BeamBuilderBase(base.OptionBuilderBase):
    def __init__(self):
        self.energies_eV = set()
        self.particles = set()

    def __len__(self):
        it = [len(self.energies_eV), len(self.particles) or 1]
        return functools.reduce(operator.mul, it)

    def add_energy_eV(self, energy_eV):
        self.energies_eV.add(energy_eV)

    def add_energy_keV(self, energy_keV):
        self.energies_eV.add(energy_keV * 1e3)

    def add_particle(self, particle):
        self.particles.add(particle)


def convert_diameter_fwhm_to_sigma(diameter):
    """
    Converts a beam diameter expressed as 2-sigma of a Gaussian distribution
    (radius = sigma) to a beam diameter expressed as the full with at half
    maximum (FWHM).

    :arg diameter: FWHM diameter.
    """
    # d_{FWHM} = 1.177411 (2\sigma)
    return diameter / 1.177411


def convert_diameter_sigma_to_fwhm(diameter):
    """
    Converts a beam diameter expressed as the full with at half maximum (FWHM)
    to a beam diameter expressed as 2-sigma of a Gaussian distribution
    (radius = sigma).

    :arg diameter: 2-sigma diameter diameter.
    """
    # d_{FWHM} = 1.177411 (2\sigma)
    return diameter * 1.177411

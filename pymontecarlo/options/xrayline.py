""""""

# Standard library modules.
from operator import attrgetter

# Third party modules.
import pyxray

# Local modules.
import pymontecarlo.options.base as base

# Globals and constants variables.

KNOWN_XRAYTRANSITIONS = [
    pyxray.xray_transition("Ka1"),
    pyxray.xray_transition("Kb1"),
    pyxray.xray_transition("La1"),
    pyxray.xray_transition("Lb1"),
    pyxray.xray_transition("Ll"),
    pyxray.xray_transition("Ma1"),
    pyxray.xray_transition("M4-N2"),  # Mz
]


def find_known_xray_lines(zs, minimum_energy_eV=0.0, maximum_energy_eV=float("inf")):
    xray_lines = []

    for z in zs:
        for xraytransition in pyxray.element_xray_transitions(z):
            if xraytransition not in KNOWN_XRAYTRANSITIONS:
                continue

            xray_line = pyxray.xray_line(z, xraytransition)
            if minimum_energy_eV <= xray_line.energy_eV <= maximum_energy_eV:
                xray_lines.append(xray_line)

    return xray_lines


class LazyLowestEnergyXrayLine(base.LazyOptionBase):

    ENERGY_TOLERANCE_eV = 0.1

    def __init__(self, minimum_energy_eV=0.0):
        super().__init__()
        self.minimum_energy_eV = minimum_energy_eV

    def __eq__(self, other):
        return super().__eq__(other) and base.isclose(
            self.minimum_energy_eV,
            other.minimum_energy_eV,
            abs_tol=self.ENERGY_TOLERANCE_eV,
        )

    def apply(self, parent_option, options):
        zs = options.sample.atomic_numbers
        if not zs:
            raise ValueError("Cannot find x-ray line, no material in sample")

        beam_energy_eV = base.apply_lazy(options.beam.energy_eV, options.beam, options)
        xraylines = find_known_xray_lines(
            zs,
            minimum_energy_eV=self.minimum_energy_eV,
            maximum_energy_eV=beam_energy_eV,
        )
        if not xraylines:
            raise ValueError("Cannot find x-ray line, no x-ray line found")

        return min(xraylines, key=attrgetter("energy_eV"))

    # region HDF5

    ATTR_MINIMUM_ENERGY = "minimum energy"

    @classmethod
    def parse_hdf5(cls, group):
        minimum_energy_eV = cls._parse_hdf5(group, cls.ATTR_MINIMUM_ENERGY, float)
        return cls(minimum_energy_eV)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_MINIMUM_ENERGY, self.minimum_energy_eV)

    # endregion

    # region Document

    def convert_document(self, builder):
        super().convert_document(builder)
        builder.add_text(
            "Lowest energy X-ray line between {:.1f} eV and beam energy".format(
                self.minimum_energy_eV
            )
        )


# endregion

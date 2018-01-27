""""""

# Standard library modules.

# Third party modules.
import pyxray

import numpy as np

# Local modules.
from pymontecarlo.formats.hdf5.handler import HDF5Handler

# Globals and constants variables.

class XrayLineHDF5HandlerMixin:

    GROUP_XRAYLINES = 'xraylines'

    def _parse_xrayline_internal(self, group, ref_xrayline):
        group_xrayline = group.file[ref_xrayline]
        return self._parse_hdf5handlers(group_xrayline)

    def _require_xraylines_group(self, group):
        return group.file.require_group(self.GROUP_XRAYLINES)

    def _convert_xrayline_internal(self, xrayline, group):
        group_xraylines = self._require_xraylines_group(group)

        name = xrayline.iupac
        if name in group_xraylines:
            return group_xraylines[name]

        group_xrayline = group_xraylines.create_group(name)

        self._convert_hdf5handlers(xrayline, group_xrayline)

        return group_xrayline

class XrayLineHDF5Handler(HDF5Handler):

    ATTR_ATOMIC_NUMBER = 'atomic_number'
    DATASET_TRANSITIONS = 'transitions'
    ATTR_IUPAC = 'iupac'
    ATTR_SIEGBAHN = 'siegbahn'
    ATTR_ENERGY = 'energy'

    def _parse_element(self, group):
        return int(group.attrs[self.ATTR_ATOMIC_NUMBER])

    def _parse_transitions(self, group):
        dataset = group[self.DATASET_TRANSITIONS]

        transitions = []
        for n0, l0, j0_n, n1, l1, j1_n in dataset:
            src = pyxray.AtomicSubshell(n0, l0, j0_n)
            dst = pyxray.AtomicSubshell(n1, l1, j1_n)
            transitions.append(pyxray.XrayTransition(src, dst))

        return transitions

    def _parse_iupac(self, group):
        return group.attrs[self.ATTR_IUPAC]

    def _parse_siebahn(self, group):
        return group.attrs[self.ATTR_SIEGBAHN]

    def _parse_energy(self, group):
        return float(group.attrs[self.ATTR_ENERGY])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_ATOMIC_NUMBER in group.attrs and \
            self.DATASET_TRANSITIONS in group and \
            self.ATTR_IUPAC in group.attrs and \
            self.ATTR_SIEGBAHN in group.attrs and \
            self.ATTR_ENERGY in group.attrs

    def parse(self, group):
        element = self._parse_element(group)
        transitions = self._parse_transitions(group)
        iupac = self._parse_iupac(group)
        siegbahn = self._parse_siebahn(group)
        energy_eV = self._parse_energy(group)
        return self.CLASS(element, transitions, iupac, siegbahn, energy_eV)

    def _convert_element(self, element, group):
        group.attrs[self.ATTR_ATOMIC_NUMBER] = element.atomic_number

    def _convert_transitions(self, transitions, group):
        data = []
        for transition in transitions:
            src = transition.source_subshell
            dst = transition.destination_subshell
            data.append([src.n, src.l, src.j_n, dst.n, dst.l, dst.j_n])

        group.create_dataset(self.DATASET_TRANSITIONS, data=data, dtype=np.byte)

    def _convert_iupac(self, iupac, group):
        group.attrs[self.ATTR_IUPAC] = iupac

    def _convert_siegbahn(self, siegbahn, group):
        group.attrs[self.ATTR_SIEGBAHN] = siegbahn

    def _convert_energy_eV(self, energy_eV, group):
        group.attrs[self.ATTR_ENERGY] = energy_eV

    def convert(self, xrayline, group):
        super().convert(xrayline, group)
        self._convert_element(xrayline.element, group)
        self._convert_transitions(xrayline.transitions, group)
        self._convert_iupac(xrayline.iupac, group)
        self._convert_siegbahn(xrayline.siegbahn, group)
        self._convert_energy_eV(xrayline.energy_eV, group)

    @property
    def CLASS(self):
        return pyxray.XrayLine

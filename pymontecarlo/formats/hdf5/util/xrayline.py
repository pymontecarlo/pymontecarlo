""""""

# Standard library modules.

# Third party modules.
import pyxray

import numpy as np

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.util.xrayline import XrayLine

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

        name = xrayline.name
        if name in group_xraylines:
            return group_xraylines[name]

        group_xrayline = group_xraylines.create_group(name)

        self._convert_hdf5handlers(xrayline, group_xrayline)

        return group_xrayline

class XrayLineHDF5Handler(HDF5Handler):

    ATTR_ATOMIC_NUMBER = 'atomic_number'
    DATASET_TRANSITIONS = 'transitions'

    def _parse_element(self, group):
        return int(group.attrs[self.ATTR_ATOMIC_NUMBER])

    def _parse_line(self, group):
        dataset = group[self.DATASET_TRANSITIONS]

        xraytransitions = []
        for n0, l0, j0_n, n1, l1, j1_n in dataset:
            src = pyxray.AtomicSubshell(n0, l0, j0_n)
            dst = pyxray.AtomicSubshell(n1, l1, j1_n)
            xraytransitions.append(pyxray.XrayTransition(src, dst))

        if len(xraytransitions) == 1:
            line = xraytransitions[0]
        else:
            line = pyxray.XrayTransitionSet(xraytransitions)

        return line

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_ATOMIC_NUMBER in group.attrs and \
            self.DATASET_TRANSITIONS in group

    def parse(self, group):
        element = self._parse_element(group)
        line = self._parse_line(group)
        return self.CLASS(element, line)

    def _convert_element(self, element, group):
        group.attrs[self.ATTR_ATOMIC_NUMBER] = element.atomic_number

    def _convert_line(self, line, group):
        if hasattr(line, 'source_subshell'):
            xraytransitions = [line]
        else:
            xraytransitions = line.transitions

        data = []
        for xraytransition in xraytransitions:
            src = xraytransition.source_subshell
            dst = xraytransition.destination_subshell
            data.append([src.n, src.l, src.j_n, dst.n, dst.l, dst.j_n])

        group.create_dataset(self.DATASET_TRANSITIONS, data=data, dtype=np.byte)

    def convert(self, xrayline, group):
        super().convert(xrayline, group)
        self._convert_element(xrayline.element, group)
        self._convert_line(xrayline.line, group)

    @property
    def CLASS(self):
        return XrayLine

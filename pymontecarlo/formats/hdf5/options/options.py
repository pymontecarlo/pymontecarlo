""""""

# Standard library modules.

# Third party modules.
import h5py

import numpy as np

# Local modules.
from pymontecarlo.formats.hdf5.handler import HDF5HandlerBase
from pymontecarlo.formats.hdf5.options.program.base import ProgramHDF5HandlerMixin
from pymontecarlo.formats.hdf5.options.beam.base import BeamHDF5HandlerMixin
from pymontecarlo.formats.hdf5.options.sample.base import SampleHDF5HandlerMixin
from pymontecarlo.formats.hdf5.options.analysis.base import AnalysisHDF5HandlerMixin
from pymontecarlo.options.options import Options

# Globals and constants variables.

class OptionsHDF5Handler(HDF5HandlerBase,
                         ProgramHDF5HandlerMixin,
                         BeamHDF5HandlerMixin,
                         SampleHDF5HandlerMixin,
                         AnalysisHDF5HandlerMixin):

    ATTR_PROGRAM = 'program'
    ATTR_BEAM = 'beam'
    ATTR_SAMPLE = 'sample'
    ATTR_ANALYSES = 'analyses'
    ATTR_TAGS = 'tags'

    def _parse_program(self, group):
        ref_program = group.attrs[self.ATTR_PROGRAM]
        return self._parse_program_internal(group, ref_program)

    def _parse_beam(self, group):
        ref_beam = group.attrs[self.ATTR_BEAM]
        return self._parse_beam_internal(group, ref_beam)

    def _parse_sample(self, group):
        ref_sample = group.attrs[self.ATTR_SAMPLE]
        return self._parse_sample_internal(group, ref_sample)

    def _parse_analyses(self, group):
        analyses = []
        for ref_analysis in group.attrs[self.ATTR_ANALYSES]:
            analyses.append(self._parse_analysis_internal(group, ref_analysis))
        return analyses

    def _parse_tags(self, group):
        return list(group.attrs[self.ATTR_TAGS])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_PROGRAM in group.attrs and \
            self.ATTR_BEAM in group.attrs and \
            self.ATTR_SAMPLE in group.attrs and \
            self.ATTR_ANALYSES in group.attrs and \
            self.ATTR_TAGS in group.attrs

    def parse(self, group):
        program = self._parse_program(group)
        beam = self._parse_beam(group)
        sample = self._parse_sample(group)
        analyses = self._parse_analyses(group)
        tags = self._parse_tags(group)
        return self.CLASS(program, beam, sample, analyses, tags)

    def _convert_program(self, program, group):
        group_program = self._convert_program_internal(program, group)
        group.attrs[self.ATTR_PROGRAM] = group_program.ref

    def _convert_beam(self, beam, group):
        group_beam = self._convert_beam_internal(beam, group)
        group.attrs[self.ATTR_BEAM] = group_beam.ref

    def _convert_sample(self, sample, group):
        group_sample = self._convert_sample_internal(sample, group)
        group.attrs[self.ATTR_SAMPLE] = group_sample.ref

    def _convert_analyses(self, analyses, group):
        refs = []
        for analysis in analyses:
            group_analysis = self._convert_analysis_internal(analysis, group)
            refs.append(group_analysis.ref)

        dtype = h5py.special_dtype(ref=h5py.Reference)
        group.attrs.create(self.ATTR_ANALYSES, np.array(refs), dtype=dtype)

    def _convert_tags(self, tags, group):
        dtype = h5py.special_dtype(vlen=str)
        group.attrs.create(self.ATTR_TAGS, np.array(tags), dtype=dtype)

    def convert(self, options, group):
        super().convert(options, group)
        self._convert_program(options.program, group)
        self._convert_beam(options.beam, group)
        self._convert_sample(options.sample, group)
        self._convert_analyses(options.analyses, group)
        self._convert_tags(options.tags, group)

    @property
    def CLASS(self):
        return Options

""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.base import HDF5Handler
from pymontecarlo.fileformat.options.material import MaterialHDF5HandlerMixin
from pymontecarlo.options.options import Options

# Globals and constants variables.

class OptionsHDF5Handler(HDF5Handler):

    GROUP_PROGRAM = 'program'
    GROUP_BEAM = 'beam'
    GROUP_SAMPLE = 'sample'
    GROUP_ANALYSES = 'analyses'
    GROUP_LIMITS = 'limits'
    GROUP_MODELS = 'models'

    GROUP_DETECTORS = 'detectors'
    GROUP_MATERIALS = MaterialHDF5HandlerMixin.GROUP_MATERIALS

    def _parse_program(self, group):
        group_program = group[self.GROUP_PROGRAM]
        return self._parse_hdf5handlers(group_program)

    def _parse_beam(self, group):
        group_beam = group[self.GROUP_BEAM]
        return self._parse_hdf5handlers(group_beam)

    def _parse_sample(self, group):
        group_sample = group[self.GROUP_SAMPLE]
        return self._parse_hdf5handlers(group_sample)

    def _parse_analysis(self, group):
        return self._parse_hdf5handlers(group)

    def _parse_analyses(self, group):
        group_analyses = group[self.GROUP_ANALYSES]

        analyses = []
        for group_analysis in group_analyses.values():
            analyses.append(self._parse_analysis(group_analysis))

        return analyses

    def _parse_limit(self, group):
        return self._parse_hdf5handlers(group)

    def _parse_limits(self, group):
        group_limits = group[self.GROUP_LIMITS]

        limits = []
        for group_limit in group_limits.values():
            limits.append(self._parse_limit(group_limit))

        return limits

    def _parse_model(self, group):
        return self._parse_hdf5handlers(group)

    def _parse_models(self, group):
        group_models = group[self.GROUP_MODELS]

        models = []
        for group_model in group_models.values():
            models.append(self._parse_model(group_model))

        return models

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.GROUP_PROGRAM in group and \
            self.GROUP_BEAM in group and \
            self.GROUP_SAMPLE in group and \
            self.GROUP_ANALYSES in group and \
            self.GROUP_LIMITS in group and \
            self.GROUP_MODELS in group

    def parse(self, group):
        program = self._parse_program(group)
        beam = self._parse_beam(group)
        sample = self._parse_sample(group)
        analyses = self._parse_analyses(group)
        limits = self._parse_limits(group)
        models = self._parse_models(group)
        return self.CLASS(program, beam, sample, analyses, limits, models)

    def _convert_program(self, program, group):
        group_program = group.create_group(self.GROUP_PROGRAM)
        self._convert_hdf5handlers(program, group_program)

    def _convert_beam(self, beam, group):
        group_beam = group.create_group(self.GROUP_BEAM)
        self._convert_hdf5handlers(beam, group_beam)

    def _convert_sample(self, sample, group):
        group_sample = group.create_group(self.GROUP_SAMPLE)
        self._convert_hdf5handlers(sample, group_sample)

    def _convert_analysis(self, analysis, group):
        name = str(id(analysis))
        group_analysis = group.create_group(name)
        self._convert_hdf5handlers(analysis, group_analysis)

    def _convert_analyses(self, analyses, group):
        group_analyses = group.create_group(self.GROUP_ANALYSES)
        for analysis in analyses:
            self._convert_analysis(analysis, group_analyses)

    def _convert_limit(self, limit, group):
        name = str(id(limit))
        group_limit = group.create_group(name)
        self._convert_hdf5handlers(limit, group_limit)

    def _convert_limits(self, limits, group):
        group_limits = group.create_group(self.GROUP_LIMITS)
        for limit in limits:
            self._convert_analysis(limit, group_limits)

    def _convert_model(self, model, group):
        name = str(id(model))
        group_model = group.create_group(name)
        self._convert_hdf5handlers(model, group_model)

    def _convert_models(self, models, group):
        group_models = group.create_group(self.GROUP_MODELS)
        for model in models:
            self._convert_model(model, group_models)

    def convert(self, options, group):
        super().convert(options, group)

        group.require_group(self.GROUP_MATERIALS)
        group.require_group(self.GROUP_DETECTORS)

        self._convert_program(options.program, group)
        self._convert_beam(options.beam, group)
        self._convert_sample(options.sample, group)
        self._convert_analyses(options.analyses, group)
        self._convert_limits(options.limits, group)
        self._convert_models(options.models, group)

    @property
    def CLASS(self):
        return Options

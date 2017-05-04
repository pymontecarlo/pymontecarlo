""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.formats.hdf5.options.detector.base import DetectorHDF5HandlerMixin

# Globals and constants variables.

class AnalysisHDF5HandlerMixin:

    GROUP_ANALYSES = 'analyses'

    def _parse_analysis_internal(self, group, ref_analysis):
        group_analysis = group.file[ref_analysis]
        return self._parse_hdf5handlers(group_analysis)

    def _require_analyses_group(self, group):
        return group.file.require_group(self.GROUP_ANALYSES)

    def _convert_analysis_internal(self, analysis, group):
        group_analyses = self._require_analyses_group(group)

        name = '{} [{:d}]'.format(analysis.__class__.__name__, id(analysis))
        if name in group_analyses:
            return group_analyses[name]

        group_analysis = group_analyses.create_group(name)

        self._convert_hdf5handlers(analysis, group_analysis)

        return group_analysis

class AnalysisHDF5Handler(HDF5Handler, DetectorHDF5HandlerMixin):
    pass
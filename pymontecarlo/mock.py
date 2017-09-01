""""""

# Standard library modules.
import os
import json
import time

# Third party modules.

# Local modules.
from pymontecarlo.options.beam.gaussian import GaussianBeam
from pymontecarlo.options.beam.cylindrical import CylindricalBeam
from pymontecarlo.options.sample.base import Sample
from pymontecarlo.options.sample.substrate import SubstrateSample
from pymontecarlo.options.sample.inclusion import InclusionSample
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample
from pymontecarlo.options.sample.sphere import SphereSample
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.options.detector.photon import PhotonDetector
from pymontecarlo.options.program.base import Program
from pymontecarlo.options.program.expander import Expander, expand_to_single, expand_analyses_to_single_detector
from pymontecarlo.options.program.validator import Validator
from pymontecarlo.options.program.exporter import Exporter
from pymontecarlo.options.program.worker import Worker
from pymontecarlo.options.program.importer import Importer
from pymontecarlo.formats.hdf5.options.program.base import ProgramHDF5Handler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.formats.series.options.program.base import ProgramSeriesHandler
from pymontecarlo.formats.html.options.program.base import ProgramHtmlHandler

# Globals and constants variables.

class SampleMock(Sample):

    @property
    def materials(self):
        return []

class ExpanderMock(Expander):

    def expand_analyses(self, analyses):
        return expand_analyses_to_single_detector(analyses)

    def expand_limits(self, limits):
        return expand_to_single(limits)

    def expand_models(self, models):
        return expand_to_single(models)

class ValidatorMock(Validator):

    def __init__(self):
        super().__init__()

        self.beam_validate_methods[CylindricalBeam] = self._validate_beam_cylindrical
        self.beam_validate_methods[GaussianBeam] = self._validate_beam_gaussian

        self.sample_validate_methods[SubstrateSample] = self._validate_sample_substrate
        self.sample_validate_methods[InclusionSample] = self._validate_sample_inclusion
        self.sample_validate_methods[HorizontalLayerSample] = self._validate_sample_horizontallayers
        self.sample_validate_methods[VerticalLayerSample] = self._validate_sample_verticallayers
        self.sample_validate_methods[SphereSample] = self._validate_sample_sphere

        self.analysis_validate_methods[PhotonIntensityAnalysis] = self._validate_analysis_photonintensity
        self.analysis_validate_methods[KRatioAnalysis] = self._validate_analysis_kratio

        self.valid_models[ElasticCrossSectionModel] = [ElasticCrossSectionModel.RUTHERFORD, ElasticCrossSectionModel.MOTT_CZYZEWSKI1990]
        self.default_models[ElasticCrossSectionModel] = ElasticCrossSectionModel.RUTHERFORD

    def _validate_program(self, program, options, errors):
        elastic_cross_section_model = self._validate_model(program.elastic_cross_section_model, options, errors)
        return ProgramMock(program.foo, elastic_cross_section_model)

class ExporterMock(Exporter):

    def __init__(self):
        super().__init__()
        self.beam_export_methods[GaussianBeam] = self._export_beam_gaussian
        self.sample_export_methods[SubstrateSample] = self._export_sample_substrate
        self.detector_export_methods[PhotonDetector] = self._export_detector_photon
        self.analysis_export_methods[PhotonIntensityAnalysis] = self._export_analysis_photonintensity

    def _export(self, options, dirpath, errors):
        outdict = {}
        self._run_exporters(options, errors, outdict)

        filepath = os.path.join(dirpath, 'sim.json')
        with open(filepath, 'w') as fp:
            json.dump(outdict, fp)

    def _export_program(self, program, options, errors, outdict):
        outdict.setdefault('program', {})
        outdict['program']['foo'] = program.foo
        outdict['program']['elastic_cross_section_model'] = str(program.elastic_cross_section_model)

    def _export_beam_gaussian(self, beam, options, errors, outdict):
        outdict['beam'] = 'gaussian'

    def _export_sample_substrate(self, sample, options, errors, outdict):
        outdict['sample'] = 'substrate'

    def _export_detector_photon(self, detect, options, errors, outdict):
        outdict.setdefault('photon', []).append('photon')

    def _export_analysis_photonintensity(self, analysis, options, errors, outdict):
        outdict.setdefault('analyses', []).append('photon intensity')

class WorkerMock(Worker):

    def run(self, token, simulation, outputdir):
        options = simulation.options
        program = options.program
        exporter = program.create_exporter()

        exporter.export(options, outputdir)

        token.update(0.0, 'Started')
        for _ in range(10):
            if token.cancelled():
                break
            time.sleep(0.01)

        token.update(1.0, 'Done')

class ImporterMock(Importer):

    def _import(self, options, dirpath, errors):
        return []

class ProgramMock(Program):

    def __init__(self,
                 foo=None,
                 elastic_cross_section_model=ElasticCrossSectionModel.RUTHERFORD):
        super().__init__('mock')
        self.foo = foo
        self.elastic_cross_section_model = elastic_cross_section_model

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.foo == other.foo and \
            self.elastic_cross_section_model == other.elastic_cross_section_model

    def create_expander(self):
        return ExpanderMock()

    def create_validator(self):
        return ValidatorMock()

    def create_exporter(self):
        return ExporterMock()

    def create_importer(self):
        return ImporterMock()

    def create_worker(self):
        return WorkerMock()

class ProgramHDF5HandlerMock(ProgramHDF5Handler):

    ATTR_FOO = 'foo'
    ATTR_ELASTIC_CROSS_SECTION_MODEL = 'elastic_cross_section_model'

    def _parse_foo(self, group):
        return group.attrs[self.ATTR_FOO]

    def _parse_elastic_cross_section_model(self, group):
        ref_model = group.attrs[self.ATTR_ELASTIC_CROSS_SECTION_MODEL]
        return self._parse_model_internal(group, ref_model)

    def parse(self, group):
        program = super().parse(group)
        program.foo = self._parse_foo(group)
        program.elastic_cross_section_model = self._parse_elastic_cross_section_model(group)
        return program

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_FOO in group.attrs

    def _convert_foo(self, foo, group):
        group.attrs[self.ATTR_FOO] = foo

    def _convert_elastic_cross_section_model(self, model, group):
        group_model = self._convert_model_internal(model, group)
        group.attrs[self.ATTR_ELASTIC_CROSS_SECTION_MODEL] = group_model.ref

    def convert(self, program, group):
        super().convert(program, group)
        self._convert_foo(program.foo, group)
        self._convert_elastic_cross_section_model(program.elastic_cross_section_model, group)

    @property
    def CLASS(self):
        return ProgramMock

class ProgramSeriesHandlerMock(ProgramSeriesHandler):

    def convert(self, program):
        s = super().convert(program)

        column = NamedSeriesColumn('foo', 'foo')
        s[column] = program.foo

        s_model = self._find_and_convert(program.elastic_cross_section_model)
        s = s.append(s_model)

        return s

    @property
    def CLASS(self):
        return ProgramMock

class ProgramHtmlHandlerMock(ProgramHtmlHandler):

    def convert(self, program, settings, level=1):
        root = super().convert(program, settings, level)

        dl = root.getElementsByTagName('dl')[-1]
        dl += self._create_description(settings, 'Foo', program.foo)

        root += self._find_and_convert(program.elastic_cross_section_model, settings, level + 1).children

        return root

    @property
    def CLASS(self):
        return ProgramMock

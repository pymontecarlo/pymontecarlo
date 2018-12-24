""""""

# Standard library modules.
import os
import json
import time
import itertools
import operator
import functools

# Third party modules.

# Local modules.
from pymontecarlo.options.beam.gaussian import GaussianBeam
from pymontecarlo.options.beam.cylindrical import CylindricalBeam
from pymontecarlo.options.sample.base import SampleBase
from pymontecarlo.options.sample.substrate import SubstrateSample
from pymontecarlo.options.sample.inclusion import InclusionSample
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample
from pymontecarlo.options.sample.sphere import SphereSample
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.options.detector.photon import PhotonDetector
from pymontecarlo.options.program.base import ProgramBase, ProgramBuilderBase
from pymontecarlo.options.program.expander import ExpanderBase, expand_to_single, expand_analyses_to_single_detector
from pymontecarlo.options.program.validator import ValidatorBase
from pymontecarlo.options.program.exporter import ExporterBase
from pymontecarlo.options.program.worker import WorkerBase
from pymontecarlo.options.program.importer import ImporterBase
from pymontecarlo.formats.hdf5.options.program.base import ProgramHDF5HandlerBase
from pymontecarlo.formats.series.options.program.base import ProgramSeriesHandlerBase
from pymontecarlo.formats.document.options.program.base import ProgramDocumentHandlerBase

# Globals and constants variables.

class SampleMock(SampleBase):

    @property
    def materials(self):
        return []

class ExpanderMock(ExpanderBase):

    def expand_analyses(self, analyses):
        return expand_analyses_to_single_detector(analyses)

    def expand_limits(self, limits):
        return expand_to_single(limits)

    def expand_models(self, models):
        return expand_to_single(models)

class ValidatorMock(ValidatorBase):

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

    def _validate_program(self, program, options, errors, warnings):
        elastic_cross_section_model = self._validate_model(program.elastic_cross_section_model, options, errors, warnings)
        return ProgramMock(program.foo, elastic_cross_section_model)

    def _validate_beam_base_energy_eV(self, energy_eV, options, errors, warnings):
        energy_eV = super()._validate_beam_base_energy_eV(energy_eV, options, errors, warnings)

        if energy_eV < 5e2:
            exc = ValueError('Beam energy must be greater or equal to 1000eV.')
            errors.add(exc)

        return energy_eV

class ExporterMock(ExporterBase):

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

class WorkerMock(WorkerBase):

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

class ImporterMock(ImporterBase):

    def _import(self, options, dirpath, errors, warnings):
        return []

class ProgramMock(ProgramBase):

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

class ProgramBuilderMock(ProgramBuilderBase):

    def __init__(self):
        self.foos = set()
        self.elastic_cross_section_models = set()

    def __len__(self):
        it = [super().__len__(),
              len(self.foos),
              len(self.elastic_cross_section_models)]
        return functools.reduce(operator.mul, it)

    def add_foo(self, foo):
        self.foos.add(foo)

    def add_elastic_cross_section_model(self, model):
        self.elastic_cross_section_models.add(model)

    def build(self):
        product = itertools.product(self.foos, self.elastic_cross_section_models)

        programs = []
        for foo, elastic_cross_section_model in product:
            program = ProgramMock(foo, elastic_cross_section_model)
            programs.append(program)

        return programs

class ProgramHDF5HandlerMock(ProgramHDF5HandlerBase):

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

class ProgramSeriesHandlerMock(ProgramSeriesHandlerBase):

    def convert(self, program, builder):
        super().convert(program, builder)
        builder.add_column('foo', 'foo', program.foo)
        builder.add_object(program.elastic_cross_section_model)

    @property
    def CLASS(self):
        return ProgramMock

class ProgramDocumentHandlerMock(ProgramDocumentHandlerBase):

    def convert(self, program, builder):
        super().convert(program, builder)

        description = builder.require_description('program')
        description.add_item('Foo', program.foo)

        section = builder.add_section()
        section.add_title('Models')
        section.add_object(program.elastic_cross_section_model)

    @property
    def CLASS(self):
        return ProgramMock

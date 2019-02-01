""""""

# Standard library modules.
import os
import sys
import json
import itertools
import operator
import functools
import asyncio

# Third party modules.

# Local modules.
from pymontecarlo.options.beam import GaussianBeam, CylindricalBeam
from pymontecarlo.options.sample.base import SampleBase
from pymontecarlo.options.sample import SubstrateSample, InclusionSample, SphereSample, HorizontalLayerSample, VerticalLayerSample
from pymontecarlo.options.model import ElasticCrossSectionModel
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.program.base import ProgramBase, ProgramBuilderBase
from pymontecarlo.options.program.expander import ExpanderBase, expand_to_single, expand_analyses_to_single_detector
from pymontecarlo.options.program.exporter import ExporterBase
from pymontecarlo.options.program.worker import WorkerBase
from pymontecarlo.options.program.importer import ImporterBase
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder
from pymontecarlo.formats.hdf5.options.program.base import ProgramHDF5HandlerBase
from pymontecarlo.formats.series.options.program.base import ProgramSeriesHandlerBase
from pymontecarlo.formats.document.options.program.base import ProgramDocumentHandlerBase
from pymontecarlo.util.process import create_startupinfo

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

class ExporterMock(ExporterBase):

    def __init__(self):
        super().__init__()
        self.beam_export_methods[GaussianBeam] = self._export_beam_gaussian
        self.beam_export_methods[CylindricalBeam] = self._export_beam_cylindrical
        self.sample_export_methods[SubstrateSample] = self._export_sample_substrate
        self.sample_export_methods[InclusionSample] = self._export_sample_inclusion
        self.sample_export_methods[SphereSample] = self._export_sample_sphere
        self.sample_export_methods[HorizontalLayerSample] = self._export_sample_horizontallayers
        self.sample_export_methods[VerticalLayerSample] = self._export_sample_verticallayers
        self.detector_export_methods[PhotonDetector] = self._export_detector_photon
        self.analysis_export_methods[PhotonIntensityAnalysis] = self._export_analysis_photonintensity
        self.analysis_export_methods[KRatioAnalysis] = self._export_analysis_kratio

    async def _export(self, options, dirpath, erracc, dry_run=False):
        outdict = {}
        self._run_exporters(options, erracc, outdict)

        if not dry_run:
            filepath = os.path.join(dirpath, 'sim.json')
            with open(filepath, 'w') as fp:
                json.dump(outdict, fp)

    def _export_program(self, program, options, erracc, outdict):
        valid_models = [ElasticCrossSectionModel.RUTHERFORD, ElasticCrossSectionModel.MOTT_CZYZEWSKI1990]
        self._export_model(program.elastic_cross_section_model, valid_models, erracc)

        outdict.setdefault('program', {})
        outdict['program']['foo'] = program.foo
        outdict['program']['elastic_cross_section_model'] = str(program.elastic_cross_section_model)

    def _export_beam_cylindrical(self, beam, options, erracc, outdict):
        super()._export_beam_cylindrical(beam, options, erracc)

        if beam.energy_eV < 5e2:
            exc = ValueError('Beam energy must be greater or equal to 500eV.')
            erracc.add_exception(exc)

        outdict['beam'] = 'cylindrical'

    def _export_beam_gaussian(self, beam, options, erracc, outdict):
        super()._export_beam_gaussian(beam, options, erracc)

        if beam.energy_eV < 5e2:
            exc = ValueError('Beam energy must be greater or equal to 500eV.')
            erracc.add_exception(exc)

        outdict['beam'] = 'gaussian'

    def _export_sample_substrate(self, sample, options, erracc, outdict):
        super()._export_sample_substrate(sample, options, erracc)

        outdict['sample'] = 'substrate'

    def _export_sample_inclusion(self, sample, options, erracc, outdict):
        super()._export_sample_inclusion(sample, options, erracc, outdict)

        outdict['sample'] = 'inclusion'

    def _export_sample_sphere(self, sample, options, erracc, outdict):
        super()._export_sample_sphere(sample, options, erracc, outdict)

        outdict['sample'] = 'sphere'

    def _export_sample_horizontallayers(self, sample, options, erracc, outdict):
        super()._export_sample_horizontallayers(sample, options, erracc, outdict)

        for layer in sample.layers:
            self._export_layer(layer, options, erracc, outdict)

        outdict['sample'] = 'horizontallayers'

    def _export_sample_verticallayers(self, sample, options, erracc, outdict):
        super()._export_sample_verticallayers(sample, options, erracc, outdict)

        for layer in sample.layers:
            self._export_layer(layer, options, erracc, outdict)

        outdict['sample'] = 'verticallayers'

    def _export_detector_photon(self, detector, options, erracc, outdict):
        super()._export_detector_photon(detector, options, erracc)

        outdict.setdefault('detectors', []).append('photon')

    def _export_analysis_photonintensity(self, analysis, options, erracc, outdict):
        super()._export_analysis_photonintensity(analysis, options, erracc)

        outdict.setdefault('analyses', []).append('photon intensity')

    def _export_analysis_kratio(self, analysis, options, erracc, outdict):
        super()._export_analysis_kratio(analysis, options, erracc)

        outdict.setdefault('analyses', []).append('kratio')

class WorkerMock(WorkerBase):

    async def _run(self, token, simulation, outputdir):
        # Export
        token.update(0.1, 'Exporting options')
        options = simulation.options

        program = options.program
        exporter = program.create_exporter()
        await exporter.export(options, outputdir)

        # Run
        token.update(0.2, 'Started')
        for i in range(10):

            args = [sys.executable, '-c', 'import os; print(os.name)']

            kwargs = {}
            kwargs['stdout'] = asyncio.subprocess.DEVNULL
            kwargs['stderr'] = asyncio.subprocess.DEVNULL
            kwargs['startupinfo'] = create_startupinfo()

            proc = await asyncio.create_subprocess_exec(*args, **kwargs)
            await proc.wait()

            await asyncio.sleep(0.01)

            token.update(0.2 + i * 6 / 100, 'Running iteration {} / 10'.format(i))

        # Import
        token.update(0.9, 'Importing results')

        for analysis in options.find_analyses(PhotonIntensityAnalysis):
            builder = EmittedPhotonIntensityResultBuilder(analysis)
            builder.add_intensity((29, 'Ka1'), 1.0, 0.1)
            builder.add_intensity((29, 'Ka2'), 2.0, 0.2)
            builder.add_intensity((29, 'Kb1'), 4.0, 0.5)
            builder.add_intensity((29, 'Kb3'), 5.0, 0.7)
            builder.add_intensity((29, 'Kb5I'), 1.0, 0.1)
            builder.add_intensity((29, 'Kb5II'), 0.5, 0.1)
            builder.add_intensity((29, 'Ll'), 3.0, 0.1)
            simulation.results.append(builder.build())

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

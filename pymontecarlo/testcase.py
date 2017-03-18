"""
Common test case for all unit tests
"""

# Standard library modules.
import os
import unittest
import math
import json
import tempfile
import shutil
import time

# Third party modules.
import pkg_resources

# Local modules.
import pymontecarlo
from pymontecarlo.program.base import Program
from pymontecarlo.program.configurator import Configurator
from pymontecarlo.program.expander import Expander, expand_to_single
from pymontecarlo.program.validator import Validator
from pymontecarlo.program.exporter import Exporter
from pymontecarlo.program.worker import Worker
from pymontecarlo.program.importer import Importer
from pymontecarlo.simulation import Simulation
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.model import RUTHERFORD, ElasticCrossSectionModel
from pymontecarlo.options.analyses import PhotonIntensityAnalysis
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder
from pymontecarlo.fileformat.base import HDF5Handler

# Globals and constants variables.

class ConfiguratorMock(Configurator):

    def prepare_parser(self, parser, program=None):
        parser.description = 'Configure Mock.'

        kwargs = {}
        kwargs['help'] = 'tore value internally'
        if program is not None:
            kwargs['default'] = program.foo
            kwargs['help'] += ' (current: {})'.format(program.foo)
        else:
            kwargs['required'] = True
        parser.add_argument('--foo', **kwargs)

    def create_program(self, namespace, clasz):
        return clasz(namespace.foo)

    def fullname(self):
        return 'Mock'

class ExpanderMock(Expander):

    def expand_analyses(self, analyses):
        return expand_to_single(analyses)

    def expand_limits(self, limits):
        return expand_to_single(limits)

    def expand_models(self, models):
        return expand_to_single(models)

class ValidatorMock(Validator):

    def __init__(self):
        super().__init__()

        self.beam_validate_methods[GaussianBeam] = self._validate_beam_gaussian

        self.sample_validate_methods[SubstrateSample] = self._validate_sample_substrate

        self.analysis_validate_methods[PhotonIntensityAnalysis] = self._validate_analysis_photonintensity

        self.limit_validate_methods[ShowersLimit] = self._validate_limit_showers

        self.model_validate_methods[ElasticCrossSectionModel] = self._validate_model_valid_models

        self.valid_models[ElasticCrossSectionModel] = [RUTHERFORD]
        self.default_models[ElasticCrossSectionModel] = RUTHERFORD

class ExporterMock(Exporter):

    def __init__(self):
        super().__init__()

        self.beam_export_methods[GaussianBeam] = self._export_beam_gaussian

        self.sample_export_methods[SubstrateSample] = self._export_sample_substrate

        self.analysis_export_methods[PhotonIntensityAnalysis] = self._export_analysis_photonintensity

        self.limit_export_methods[ShowersLimit] = self._export_limit_showers

        self.model_export_methods[ElasticCrossSectionModel] = self._export_model_generic

    def _export(self, options, dirpath, errors):
        outdict = {}
        self._run_exporters(options, errors, outdict)

        filepath = os.path.join(dirpath, 'sim.json')
        with open(filepath, 'w') as fp:
            json.dump(outdict, fp)

    def _export_beam_gaussian(self, beam, errors, outdict):
        outdict['beam'] = 'gaussian'

    def _export_sample_substrate(self, sample, errors, outdict):
        outdict['sample'] = 'substrate'

    def _export_analysis_photonintensity(self, analysis, errors, outdict):
        outdict.setdefault('analyses', []).append('photon intensity')

    def _export_limit_showers(self, limit, errors, outdict):
        outdict.setdefault('limits', []).append('showers')

    def _export_model_generic(self, model, errors, outdict):
        outdict.setdefault('models', []).append(model.name)

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

    def __init__(self, foo=None):
        self.foo = foo

    @classmethod
    def getidentifier(cls):
        return 'mock'

    @classmethod
    def create_configurator(cls):
        return ConfiguratorMock()

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

    def create_default_limits(self, options):
        return [ShowersLimit(100)]

class ProgramHDF5HandlerMock(HDF5Handler):

    CLASS = ProgramMock

    def parse(self, group):
        return super().parse(group)

    def convert(self, obj, group):
        super().convert(obj, group)

class TestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Add program HDF5 handler
        requirement = pkg_resources.Requirement('pymontecarlo')
        distribution = pkg_resources.working_set.find(requirement)
        entry_map = distribution.get_entry_map('pymontecarlo.fileformat')
        entry_map['mock'] = pkg_resources.EntryPoint('mock', 'pymontecarlo.testcase',
                                                     attrs=('ProgramHDF5HandlerMock',),
                                                     dist=distribution)

        # Add program to available programs
        entry_map = distribution.get_entry_map('pymontecarlo.program')
        entry_map['mock'] = pkg_resources.EntryPoint('mock', 'pymontecarlo.testcase',
                                                     attrs=('ProgramMock',),
                                                     dist=distribution)

        pymontecarlo.settings.reload()

        pymontecarlo.settings.preferred_xrayline_encoding = 'utf16'
        pymontecarlo.settings.preferred_xrayline_notation = 'iupac'
        pymontecarlo.settings.clear_preferred_units()

    def setUp(self):
        super().setUp()

        self.tmpdirs = []

        self.program = ProgramMock()

    def tearDown(self):
        super().tearDown()

        for tmpdir in self.tmpdirs:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def create_basic_photondetector(self):
        return PhotonDetector(math.radians(40.0))

    def create_basic_options(self):
        beam = GaussianBeam(15e3, 10e-9)
        sample = SubstrateSample(Material.pure(29))
        analyses = [PhotonIntensityAnalysis(self.create_basic_photondetector())]
        limits = [ShowersLimit(100)]
        models = [RUTHERFORD]
        return Options(self.program, beam, sample, analyses, limits, models)

    def create_basic_photonintensityresult(self):
        analysis = PhotonIntensityAnalysis(self.create_basic_photondetector())
        b = EmittedPhotonIntensityResultBuilder(analysis)
        b.add_intensity((13, 'Ka1'), 1.0, 0.1)
        b.add_intensity((13, 'Ka2'), 2.0, 0.2)
        b.add_intensity((13, 'Kb1'), 4.0, 0.5)
        b.add_intensity((13, 'Kb3'), 5.0, 0.7)
        b.add_intensity((13, 'Ll'), 3.0, 0.1)
        return b.build()

    def create_basic_simulation(self):
        options = self.create_basic_options()

        results = []
        results.append(self.create_basic_photonintensityresult())

        return Simulation(options, results)

    def create_temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        self.tmpdirs.append(tmpdir)
        return tmpdir

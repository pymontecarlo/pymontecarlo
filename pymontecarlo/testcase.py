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

# Local modules.
from pymontecarlo.settings import load_settings, _set_settings
from pymontecarlo.program.base import Program
from pymontecarlo.program.expander import Expander, expand_to_single
from pymontecarlo.program.validator import Validator
from pymontecarlo.program.exporter import Exporter
from pymontecarlo.program.worker import Worker
from pymontecarlo.simulation import Simulation
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.model import RUTHERFORD, ElasticCrossSectionModel
from pymontecarlo.options.analyses import PhotonIntensityAnalysis

# Globals and constants variables.

basepath = os.path.dirname(__file__)
filepath = os.path.join(basepath, 'testdata', 'settings.cfg')
settings = load_settings([filepath])

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

    def __init__(self):
        super().__init__()

        self._progress = 0.0
        self._status = ''

    def run(self, options):
        self._progress = 0.0
        self._status = 'Started'

        program = options.program
        exporter = program.create_exporter()

        try:
            dirpath = tempfile.mkdtemp()
            exporter.export(options, dirpath)

            time.sleep(0.1)

        finally:
            shutil.rmtree(dirpath, ignore_errors=True)

        self._progress = 1.0
        self._status = 'Done'

        return Simulation(options)

    def cancel(self):
        self._progress = 0.0
        self._status = 'Cancelled'

    @property
    def progress(self):
        return self._progress

    @property
    def status(self):
        return self._status

class ProgramMock(Program):

    def create_expander(self):
        return ExpanderMock()

    def create_validator(self):
        return ValidatorMock()

    def create_exporter(self):
        return ExporterMock()

    def create_worker(self):
        return WorkerMock()

    def create_default_limits(self, options):
        return [ShowersLimit(100)]

    @property
    def name(self):
        return 'mock'

class TestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        _set_settings(settings)

    def setUp(self):
        super().setUp()

        self.tmpdirs = []

        self.program = ProgramMock()

    def tearDown(self):
        super().tearDown()

        for tmpdir in self.tmpdirs:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def create_basic_options(self):
        beam = GaussianBeam(15e3, 10e-9)
        sample = SubstrateSample(Material.pure(29))
        analyses = [PhotonIntensityAnalysis(PhotonDetector(math.radians(40.0)))]
        limits = [ShowersLimit(100)]
        models = [RUTHERFORD]
        return Options(self.program, beam, sample, analyses, limits, models)

    def create_temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        self.tmpdirs.append(tmpdir)
        return tmpdir


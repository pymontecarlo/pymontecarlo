"""
Common test case for all unit tests
"""

# Standard library modules.
import os
import unittest
import math
import tempfile
import shutil

# Third party modules.
import pkg_resources

import h5py

# Local modules.
import pymontecarlo
from pymontecarlo.project import Project
from pymontecarlo.simulation import Simulation
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.model import ElasticCrossSectionModel
from pymontecarlo.options.analysis import PhotonIntensityAnalysis
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResultBuilder, GeneratedPhotonIntensityResultBuilder
from pymontecarlo.mock import ProgramMock

# Globals and constants variables.

class TestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Add program HDF5 handler
        requirement = pkg_resources.Requirement('pymontecarlo')
        distribution = pkg_resources.working_set.find(requirement)
        entry_map = distribution.get_entry_map('pymontecarlo.formats.hdf5')
        entry_map['mock'] = pkg_resources.EntryPoint('mock', 'pymontecarlo.mock',
                                                     attrs=('ProgramHDF5HandlerMock',),
                                                     dist=distribution)

        # Add program to available programs
        entry_map = distribution.get_entry_map('pymontecarlo.program')
        entry_map['mock'] = pkg_resources.EntryPoint('mock', 'pymontecarlo.mock',
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

    def create_basic_beam(self):
        return GaussianBeam(15e3, 10e-9)

    def create_basic_sample(self):
        return SubstrateSample(Material.pure(29))

    def create_basic_photondetector(self):
        return PhotonDetector('xray', math.radians(40.0))

    def create_basic_options(self):
        beam = self.create_basic_beam()
        sample = self.create_basic_sample()
        analyses = [PhotonIntensityAnalysis(self.create_basic_photondetector())]
        limits = [ShowersLimit(100)]
        models = [ElasticCrossSectionModel.RUTHERFORD]
        return Options(self.program, beam, sample, analyses, limits, models)

    def create_basic_photonintensityresult(self):
        analysis = PhotonIntensityAnalysis(self.create_basic_photondetector())
        b = EmittedPhotonIntensityResultBuilder(analysis)
        b.add_intensity((29, 'Ka1'), 1.0, 0.1)
        b.add_intensity((29, 'Ka2'), 2.0, 0.2)
        b.add_intensity((29, 'Kb1'), 4.0, 0.5)
        b.add_intensity((29, 'Kb3'), 5.0, 0.7)
        b.add_intensity((29, 'Kb5I'), 1.0, 0.1)
        b.add_intensity((29, 'Kb5II'), 0.5, 0.1)
        b.add_intensity((29, 'Ll'), 3.0, 0.1)
        return b.build()

    def create_basic_simulation(self):
        options = self.create_basic_options()

        results = []
        results.append(self.create_basic_photonintensityresult())

        return Simulation(options, results)

    def create_basic_project(self):
        project = Project()

        sim1 = self.create_basic_simulation()
        project.add_simulation(sim1)

        sim2 = self.create_basic_simulation()
        sim2.options.beam.energy_eV = 20e3
        project.add_simulation(sim2)

        analysis = PhotonIntensityAnalysis(self.create_basic_photondetector())
        b = GeneratedPhotonIntensityResultBuilder(analysis)
        b.add_intensity((29, 'Ka1'), 10.0, 0.1)
        b.add_intensity((29, 'Ka2'), 20.0, 0.2)
        b.add_intensity((29, 'Kb1'), 40.0, 0.5)

        sim3 = self.create_basic_simulation()
        sim3.options.beam.diameter_m = 20e-9
        sim3.results.append(b.build())
        project.add_simulation(sim3)

        return project

    def create_temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        self.tmpdirs.append(tmpdir)
        return tmpdir

    def convert_parse_hdf5handler(self, handler, obj):
        filepath = os.path.join(self.create_temp_dir(), 'object.h5')
        with h5py.File(filepath) as f:
            self.assertTrue(handler.can_convert(obj, f))
            handler.convert(obj, f)

        with h5py.File(filepath) as f:
            self.assertTrue(handler.can_parse(f))
            obj2 = handler.parse(f)

        return obj2

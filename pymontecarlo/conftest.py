""""""

# Standard library modules.
import sys
import math
import asyncio
import copy

# Third party modules.
import pytest

import pkg_resources

# Local modules.
from pymontecarlo.util.entrypoint import \
    (reset_entrypoints, ENTRYPOINT_HDF5HANDLER, ENTRYPOINT_SERIESHANDLER,
     ENTRYPOINT_DOCUMENTHANDLER)
from pymontecarlo.mock import ProgramMock
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResultBuilder, GeneratedPhotonIntensityResultBuilder
from pymontecarlo.results.kratio import KRatioResultBuilder
from pymontecarlo.simulation import Simulation
from pymontecarlo.project import Project
from pymontecarlo.settings import Settings, XrayNotation
from pymontecarlo.formats.series import SeriesBuilder
from pymontecarlo.formats.document import DocumentBuilder

# Globals and constants variables.

def pytest_runtest_setup(item):
    """
    Setup entry points for mock classes.
    """
    requirement = pkg_resources.Requirement('pymontecarlo')
    distribution = pkg_resources.working_set.find(requirement)

    # Add program mock HDF5 handler
    entry_point = pkg_resources.EntryPoint('mock', 'pymontecarlo.mock',
                                           attrs=('ProgramHDF5HandlerMock',),
                                           dist=distribution)

    entry_map = distribution.get_entry_map()
    entry_map.setdefault(ENTRYPOINT_HDF5HANDLER, {})
    entry_map[ENTRYPOINT_HDF5HANDLER]['mock'] = entry_point

    # Add program mock series handler
    entry_point = pkg_resources.EntryPoint('mock', 'pymontecarlo.mock',
                                           attrs=('ProgramSeriesHandlerMock',),
                                           dist=distribution)

    entry_map = distribution.get_entry_map()
    entry_map.setdefault(ENTRYPOINT_SERIESHANDLER, {})
    entry_map[ENTRYPOINT_SERIESHANDLER]['mock'] = entry_point

    # Add program mock document handler
    entry_point = pkg_resources.EntryPoint('mock', 'pymontecarlo.mock',
                                           attrs=('ProgramDocumentHandlerMock',),
                                           dist=distribution)

    entry_map = distribution.get_entry_map()
    entry_map.setdefault(ENTRYPOINT_DOCUMENTHANDLER, {})
    entry_map[ENTRYPOINT_DOCUMENTHANDLER]['mock'] = entry_point

    # Reset entry points
    reset_entrypoints()

@pytest.yield_fixture(scope='session')
def event_loop(request):
    """
    Run all tests using the default event loop and never closes it.
    """
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def options():
    """
    Creates basic options using the mock program.
    """
    program = ProgramMock()
    beam = GaussianBeam(15e3, 10e-9)
    sample = SubstrateSample(Material.pure(29))
    detector = PhotonDetector('xray', math.radians(40.0))
    analyses = [PhotonIntensityAnalysis(detector)]
    tags = ['basic', 'test']
    return Options(program, beam, sample, analyses, tags)

@pytest.fixture
def simulation(options):
    detector = options.detectors[0]
    results = []

    analysis = PhotonIntensityAnalysis(detector)
    builder = EmittedPhotonIntensityResultBuilder(analysis)
    builder.add_intensity((29, 'Ka1'), 1.0, 0.1)
    builder.add_intensity((29, 'Ka2'), 2.0, 0.2)
    builder.add_intensity((29, 'Kb1'), 4.0, 0.5)
    builder.add_intensity((29, 'Kb3'), 5.0, 0.7)
    builder.add_intensity((29, 'Kb5I'), 1.0, 0.1)
    builder.add_intensity((29, 'Kb5II'), 0.5, 0.1)
    builder.add_intensity((29, 'Ll'), 3.0, 0.1)
    results.append(builder.build())

    analysis = KRatioAnalysis(detector)
    builder = KRatioResultBuilder(analysis)
    builder.add_kratio((29, 'Ka1'), 1.0, 1.0)
    builder.add_kratio((29, 'Ka2'), 2.0, 1.0)
    builder.add_kratio((29, 'Kb1'), 0.5, 1.0)
    builder.add_kratio((29, 'Kb3'), 1.5, 1.0)
    builder.add_kratio((29, 'Kb5I'), 1.0, 1.0)
    builder.add_kratio((29, 'Kb5II'), 0.5, 1.0)
    builder.add_kratio((29, 'Ll'), 2.0, 1.0)
    results.append(builder.build())

    return Simulation(options, results)

@pytest.fixture
def project(simulation):
    project = Project()

    # Simulation 1
    sim1 = copy.deepcopy(simulation)
    sim1.options.tags.append('sim1')
    project.add_simulation(sim1)

    # Simulation 2
    sim2 = copy.deepcopy(simulation)
    sim2.options.tags.append('sim2')
    sim2.options.beam.energy_eV = 20e3
    project.add_simulation(sim2)

    # Simulation 3
    sim3 = copy.deepcopy(simulation)
    sim3.options.beam.diameter_m = 20e-9

    analysis = PhotonIntensityAnalysis(sim3.options.detectors[0])
    b = GeneratedPhotonIntensityResultBuilder(analysis)
    b.add_intensity((29, 'Ka1'), 10.0, 0.1)
    b.add_intensity((29, 'Ka2'), 20.0, 0.2)
    b.add_intensity((29, 'Kb1'), 40.0, 0.5)

    sim3.results.append(b.build())
    project.add_simulation(sim3)

    return project

@pytest.fixture
def settings():
    settings = Settings()
    settings.preferred_xray_notation = XrayNotation.IUPAC
    return settings

@pytest.fixture
def seriesbuilder(settings):
    return SeriesBuilder(settings)

@pytest.fixture
def documentbuilder(settings):
    return DocumentBuilder(settings)

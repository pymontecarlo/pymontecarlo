""""""

# Standard library modules.
import sys
import math
import asyncio

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
from pymontecarlo.options.analysis import PhotonIntensityAnalysis

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

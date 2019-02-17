#!/usr/bin/env python
""" """

# Standard library modules.
import math

# Third party modules.
import pytest

from uncertainties import ufloat

# Local modules.
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis.photonintensity import \
    PhotonIntensityAnalysis, PhotonIntensityAnalysisBuilder
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.

@pytest.fixture
def detector():
    return PhotonDetector('det', math.radians(40.0))

@pytest.fixture
def analysis(detector):
    return PhotonIntensityAnalysis(detector)

@pytest.fixture
def builder():
    return PhotonIntensityAnalysisBuilder()

def test_photonintensityanalysis_hdf5(analysis, tmp_path):
    testutil.assert_convert_parse_hdf5(analysis, tmp_path)

def test_photonintensityanalysis_copy(analysis):
    testutil.assert_copy(analysis)

def test_photonintensityanalysis_pickle(analysis):
    testutil.assert_pickle(analysis)

def test_photonintensityanalyis_apply(analysis, options):
    list_options = analysis.apply(options)
    assert len(list_options) == 0

def test_photonintensityanalyis_options(analysis, simulation):
    result = simulation.find_result(EmittedPhotonIntensityResult)[0]
    assert len(result) == 7

    newresult = analysis.calculate(simulation, [simulation])

    assert newresult
    assert len(result) == 10

    testutil.assert_ufloats(result[(29, 'Ka')], ufloat(3.0, 0.2236), abs=1e-4)
    testutil.assert_ufloats(result[(29, 'Kb')], ufloat(10.5, 0.8718), abs=1e-4)
    testutil.assert_ufloats(result[(29, 'K')], ufloat(13.5, 0.9), abs=1e-4)

    newresult = analysis.calculate(simulation, [simulation])
    assert not newresult

    # Just to make sure
    newresult = analysis.calculate(simulation, [simulation])
    assert not newresult

def test_photonintensityanalyisbuilder(builder):
    assert len(builder) == 0
    assert len(builder.build()) == 0

def test_photonintensityanalyisbuilder_samedetector(builder, detector):
    builder.add_photon_detector(detector)
    builder.add_photon_detector(PhotonDetector('det', math.radians(40.0)))
    assert len(builder) == 1
    assert len(builder.build()) == 1

def test_photonintensityanalyisbuilder_differentdetector(builder, detector):
    builder.add_photon_detector(detector)
    builder.add_photon_detector(PhotonDetector('det2', math.radians(41.0)))
    assert len(builder) == 2
    assert len(builder.build()) == 2

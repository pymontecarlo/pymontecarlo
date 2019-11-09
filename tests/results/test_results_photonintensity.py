#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest
import pyxray
from uncertainties import ufloat

# Local modules.
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder
from pymontecarlo.options.analysis import PhotonIntensityAnalysis
from pymontecarlo.options.detector import PhotonDetector
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def builder():
    detector = PhotonDetector("det", 1.1, 2.2)
    analysis = PhotonIntensityAnalysis(detector)

    builder = EmittedPhotonIntensityResultBuilder(analysis)
    builder.add_intensity((13, "Ka1"), 1.0, 0.1)
    builder.add_intensity((13, "Ka2"), 2.0, 0.2)
    builder.add_intensity((13, "Kb1"), 4.0, 0.5)
    builder.add_intensity((13, "Kb3"), 5.0, 0.7)
    builder.add_intensity((13, "Ll"), 3.0, 0.1)
    return builder


@pytest.fixture
def result(builder):
    return builder.build()


def _test_photonintensityresult(result):
    testutil.assert_ufloats(result.get((13, "Ka1")), ufloat(1.0, 0.1), abs=1e-4)
    testutil.assert_ufloats(result.get((14, "Ka1")), ufloat(0.0, 0.0), abs=1e-4)
    assert result.get((14, "Ka1"), None) is None


def test_photonintensityresult(result):
    _test_photonintensityresult(result)


def test_photonintensityresult_hdf5(result, tmp_path):
    result2 = testutil.assert_convert_parse_hdf5(
        result, tmp_path, assert_equality=False
    )
    _test_photonintensityresult(result2)


def test_photonintensityresult_series(result, seriesbuilder):
    result.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 18


def test_photonintensityresultbuilder(builder):
    data = builder.build()

    assert len(data) == 9
    assert pyxray.xray_line(13, "K") in data
    assert pyxray.xray_line(13, "Ka") in data
    assert pyxray.xray_line(13, "L") in data
    assert pyxray.xray_line(13, "Ll,n") in data

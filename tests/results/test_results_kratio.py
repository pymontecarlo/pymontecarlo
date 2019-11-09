#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

from uncertainties import ufloat

# Local modules.
from pymontecarlo.results.kratio import KRatioResultBuilder
from pymontecarlo.options.analysis import KRatioAnalysis
from pymontecarlo.options.detector import PhotonDetector
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def builder():
    detector = PhotonDetector("det", 1.1, 2.2)
    analysis = KRatioAnalysis(detector)

    builder = KRatioResultBuilder(analysis)
    builder.add_kratio((13, "Ka1"), 1.0, 1.0)
    builder.add_kratio((13, "Ka2"), 2.0, 1.0)
    builder.add_kratio((13, "Kb1"), 4.0, 1.0)
    builder.add_kratio((13, "Kb3"), 5.0, 1.0)
    builder.add_kratio((13, "Ll"), 3.0, 1.0)
    return builder


@pytest.fixture
def result(builder):
    return builder.build()


def _test_kratioresult(result):
    testutil.assert_ufloats(result.get((13, "Ka1")), ufloat(1.0, 0.0), abs=1e-4)
    testutil.assert_ufloats(result.get((14, "Ka1")), ufloat(0.0, 0.0), abs=1e-4)
    assert result.get((14, "Ka1"), None) is None


def test_kratioresult(result):
    _test_kratioresult(result)


def test_kratioresult_hdf5(result, tmp_path):
    result2 = testutil.assert_convert_parse_hdf5(
        result, tmp_path, assert_equality=False
    )
    _test_kratioresult(result2)


def test_kratioresult_series(result, seriesbuilder):
    result.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 18


def test_kratiobuilder(builder):
    assert len(builder.build()) == 9

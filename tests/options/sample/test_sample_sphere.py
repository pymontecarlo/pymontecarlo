#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.sample.sphere import SphereSample, SphereSampleBuilder
from pymontecarlo.options.material import Material
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)


@pytest.fixture
def sample():
    return SphereSample(COPPER, 123.456)


@pytest.fixture
def builder():
    return SphereSampleBuilder()


def test_spheresample(sample):
    assert sample.material == COPPER
    assert sample.diameter_m == pytest.approx(123.456, abs=1e-4)

    assert len(sample.materials) == 1


def test_spheresample_eq(sample):
    assert sample == SphereSample(COPPER, 123.456)
    assert sample != SphereSample(ZINC, 123.456)
    assert sample != SphereSample(COPPER, 124.456)


def test_spheresample_hdf5(sample, tmp_path):
    testutil.assert_convert_parse_hdf5(sample, tmp_path)


def test_spheresample_copy(sample):
    testutil.assert_copy(sample)


def test_spheresample_pickle(sample):
    testutil.assert_pickle(sample)


def test_spheresample_series(sample, seriesbuilder):
    sample.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 5


def test_spheresample_document(sample, documentbuilder):
    sample.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 6


def test_substratesamplebuilder(builder):
    builder.add_material(COPPER)
    builder.add_material(ZINC)
    builder.add_diameter_m(1.0)

    samples = builder.build()
    assert len(builder) == 2
    assert len(samples) == 2

    for sample in samples:
        assert sample.tilt_rad == pytest.approx(0.0, abs=1e-4)
        assert sample.azimuth_rad == pytest.approx(0.0, abs=1e-4)

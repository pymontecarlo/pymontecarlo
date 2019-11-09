#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.sample.substrate import (
    SubstrateSample,
    SubstrateSampleBuilder,
)
from pymontecarlo.options.material import Material
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)


@pytest.fixture
def sample():
    return SubstrateSample(COPPER)


@pytest.fixture
def builder():
    return SubstrateSampleBuilder()


def test_substratesample(sample):
    assert sample.material == COPPER

    assert len(sample.materials) == 1


def test_substratesample_eq(sample):
    assert sample == SubstrateSample(COPPER)
    assert sample != SubstrateSample(ZINC)
    assert sample != SubstrateSample(COPPER, 1.1)


def test_substratesample_hdf5(sample, tmp_path):
    testutil.assert_convert_parse_hdf5(sample, tmp_path)


def test_substratesample_copy(sample):
    testutil.assert_copy(sample)


def test_substratesample_pickle(sample):
    testutil.assert_pickle(sample)


def test_substratesample_series(sample, seriesbuilder):
    sample.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 4


def test_substratesample_document(sample, documentbuilder):
    sample.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 5


def test_substratesamplebuilder_twomaterials(builder):
    builder.add_material(COPPER)
    builder.add_material(ZINC)

    samples = builder.build()
    assert len(builder) == 2
    assert len(samples) == 2

    for sample in samples:
        assert sample.tilt_rad == pytest.approx(0.0, abs=1e-4)
        assert sample.azimuth_rad == pytest.approx(0.0, abs=1e-4)


def test_substratesamplebuilder_twomaterials_with_tilt(builder):
    builder.add_material(COPPER)
    builder.add_material(ZINC)
    builder.add_tilt_rad(1.1)

    samples = builder.build()
    assert len(builder) == 2
    assert len(samples) == 2

    for sample in samples:
        assert sample.tilt_rad == pytest.approx(1.1, abs=1e-4)
        assert sample.azimuth_rad == pytest.approx(0.0, abs=1e-4)


def test_substratesamplebuilder_twomaterials_with_tilt_and_azimuth(builder):
    builder.add_material(COPPER)
    builder.add_material(ZINC)
    builder.add_tilt_rad(1.1)
    builder.add_azimuth_rad(2.2)

    samples = builder.build()
    assert len(builder) == 2
    assert len(samples) == 2

    for sample in samples:
        assert sample.tilt_rad == pytest.approx(1.1, abs=1e-4)
        assert sample.azimuth_rad == pytest.approx(2.2, abs=1e-4)


def test_substratesamplebuilder_twomaterials_twoazimuths(builder):
    builder.add_material(COPPER)
    builder.add_material(ZINC)
    builder.add_tilt_rad(1.1)
    builder.add_azimuth_rad(2.2)
    builder.add_azimuth_rad(2.3)

    samples = builder.build()
    assert len(builder) == 4
    assert len(samples) == 4


def test_substratesamplebuilder_nomaterial(builder):
    builder.add_tilt_rad(1.1)
    builder.add_azimuth_rad(2.2)
    builder.add_azimuth_rad(2.3)

    samples = builder.build()
    assert len(builder) == 0
    assert len(samples) == 0

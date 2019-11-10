#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.sample.inclusion import (
    InclusionSample,
    InclusionSampleBuilder,
)
from pymontecarlo.options.material import Material
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)


@pytest.fixture
def sample():
    return InclusionSample(COPPER, ZINC, 123.456)


@pytest.fixture
def builder():
    return InclusionSampleBuilder()


def test_inclusionsample(sample):
    assert sample.substrate_material == COPPER
    assert sample.inclusion_material == ZINC
    assert sample.inclusion_diameter_m == pytest.approx(123.456, abs=1e-4)

    assert len(sample.materials) == 2


def test_inclusionsample_eq(sample):
    assert sample == InclusionSample(COPPER, ZINC, 123.456)
    assert sample != InclusionSample(COPPER, GALLIUM, 123.456)
    assert sample != InclusionSample(GALLIUM, ZINC, 123.456)
    assert sample != InclusionSample(COPPER, ZINC, 124.456)


def test_inclusionsample_hdf5(sample, tmp_path):
    testutil.assert_convert_parse_hdf5(sample, tmp_path)


def test_inclusionsample_copy(sample):
    testutil.assert_copy(sample)


def test_inclusionample_pickle(sample):
    testutil.assert_pickle(sample)


def test_inclusionample_series(sample, seriesbuilder):
    sample.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 7


def test_inclusionample_document(sample, documentbuilder):
    sample.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 7


def test_inclusionsamplebuilder(builder):
    builder.add_substrate_material(COPPER)
    builder.add_substrate_material(ZINC)
    builder.add_inclusion_material(GALLIUM)
    builder.add_inclusion_diameter_m(1.0)
    builder.add_inclusion_diameter_m(2.0)

    samples = builder.build()
    assert len(builder) == 4
    assert len(samples) == 4

    for sample in samples:
        assert sample.tilt_rad == pytest.approx(0.0, abs=1e-4)
        assert sample.azimuth_rad == pytest.approx(0.0, abs=1e-4)

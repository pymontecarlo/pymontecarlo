#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.sample.verticallayers import (
    VerticalLayerSample,
    VerticalLayerSampleBuilder,
)
from pymontecarlo.options.material import Material
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)


@pytest.fixture
def sample():
    sample = VerticalLayerSample(COPPER, ZINC)
    sample.add_layer(GERMANIUM, 100.0)
    sample.add_layer(COPPER, 200.0)
    sample.depth_m = 400.0
    return sample


@pytest.fixture
def builder():
    return VerticalLayerSampleBuilder()


def test_verticallayerssample(sample):
    assert sample.left_material == COPPER
    assert sample.right_material == ZINC

    assert len(sample.layers) == 2
    assert sample.layers[0].material == GERMANIUM
    assert sample.layers[0].thickness_m == pytest.approx(100, abs=1e-4)
    assert sample.layers[1].material == COPPER
    assert sample.layers[1].thickness_m == pytest.approx(200, abs=1e-4)

    assert sample.depth_m == pytest.approx(400, abs=1e-4)

    assert len(sample.materials) == 3


def test_verticallayerssample_layers_xpositions_m(sample):
    xpositions_m = sample.layers_xpositions_m
    assert len(xpositions_m) == len(sample.layers)

    xmin_m, xmax_m = xpositions_m[0]
    assert xmin_m == pytest.approx(-150, abs=1e-4)
    assert xmax_m == pytest.approx(-50, abs=1e-4)

    xmin_m, xmax_m = xpositions_m[1]
    assert xmin_m == pytest.approx(-50, abs=1e-4)
    assert xmax_m == pytest.approx(150, abs=1e-4)


def test_verticallayerssample_eq(sample):
    other = VerticalLayerSample(COPPER, ZINC)
    other.add_layer(GERMANIUM, 100.0)
    other.add_layer(COPPER, 200.0)
    other.depth_m = 400.0
    assert sample == other

    other = VerticalLayerSample(COPPER, ZINC)
    other.add_layer(GERMANIUM, 100.0)
    other.add_layer(COPPER, 200.0)
    assert sample != other

    other = VerticalLayerSample(GERMANIUM, ZINC)
    other.add_layer(GALLIUM, 500.0)
    assert sample != other


def test_verticallayerssample_hdf5(sample, tmp_path):
    testutil.assert_convert_parse_hdf5(sample, tmp_path)


def test_verticallayerssample_copy(sample):
    testutil.assert_copy(sample)


def test_verticallayerssample_pickle(sample):
    testutil.assert_pickle(sample)


def test_verticallayerssample_series(sample, seriesbuilder):
    sample.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 13


def test_verticallayerssample_document(sample, documentbuilder):
    sample.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 7


def test_verticallayerssamplebuilder(builder):
    builder.add_left_material(COPPER)
    builder.add_right_material(COPPER)
    builderlayer = builder.add_layer(ZINC, 10)
    builderlayer.add_material(GALLIUM)

    samples = builder.build()
    assert len(builder) == 2
    assert len(samples) == 2

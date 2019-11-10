#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.sample.horizontallayers import (
    HorizontalLayerSample,
    HorizontalLayerSampleBuilder,
)
from pymontecarlo.options.material import Material, VACUUM
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)


@pytest.fixture(params=[COPPER, None])
def sample(request):
    sample = HorizontalLayerSample(request.param)
    sample.add_layer(ZINC, 123.456)
    sample.add_layer(GALLIUM, 456.789)
    return sample


@pytest.fixture
def builder():
    return HorizontalLayerSampleBuilder()


def test_horizontallayerssample(sample):
    if sample.has_substrate():
        assert sample.substrate_material == COPPER
        assert len(sample.materials) == 3

    else:
        assert sample.substrate_material == VACUUM
        assert len(sample.materials) == 2

    assert len(sample.layers) == 2
    assert sample.layers[0].material == ZINC
    assert sample.layers[0].thickness_m == pytest.approx(123.456, abs=1e-4)
    assert sample.layers[1].material == GALLIUM
    assert sample.layers[1].thickness_m == pytest.approx(456.789, abs=1e-4)


def test_horizontallayerssample_layers_zpositions_m(sample):
    zpositions_m = sample.layers_zpositions_m
    assert len(zpositions_m) == len(sample.layers)

    zmin_m, zmax_m = zpositions_m[0]
    assert zmin_m == pytest.approx(-123.456, abs=1e-4)
    assert zmax_m == pytest.approx(0.0, abs=1e-4)

    zmin_m, zmax_m = zpositions_m[1]
    assert zmin_m == pytest.approx(-123.456 - 456.789, abs=1e-4)
    assert zmax_m == pytest.approx(-123.456, abs=1e-4)


def test_horizontallayerssample_eq(sample):
    if sample.has_substrate():
        other = HorizontalLayerSample(COPPER)
        other.add_layer(ZINC, 123.456)
        other.add_layer(GALLIUM, 456.789)
        assert sample == other

    else:
        other = HorizontalLayerSample(None)
        other.add_layer(ZINC, 123.456)
        other.add_layer(GALLIUM, 456.789)
        assert sample == other


def test_horizontallayerssample_ne(sample):
    other = HorizontalLayerSample(ZINC)
    other.add_layer(ZINC, 123.456)
    other.add_layer(GALLIUM, 456.789)
    assert sample != other

    other = HorizontalLayerSample(COPPER)
    other.add_layer(GALLIUM, 456.789)
    assert sample != other

    other = HorizontalLayerSample(COPPER)
    other.add_layer(ZINC, 9999)
    other.add_layer(GALLIUM, 456.789)
    assert sample != other


def test_horizontallayerssample_hdf5(sample, tmp_path):
    testutil.assert_convert_parse_hdf5(sample, tmp_path)


def test_horizontallayerssample_copy(sample):
    testutil.assert_copy(sample)


def test_horizontallayerssample_pickle(sample):
    testutil.assert_pickle(sample)


def test_horizontallayerssample_series(sample, seriesbuilder):
    sample.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 10 if sample.has_substrate() else 9


def test_horizontallayerssample_document(sample, documentbuilder):
    sample.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 7


def test_horizontallayerssamplebuilder(builder):
    builder.add_substrate_material(COPPER)
    layerbuilder = builder.add_layer(ZINC, 10)
    layerbuilder.add_material(GALLIUM)

    samples = builder.build()
    assert len(builder) == 2
    assert len(samples) == 2

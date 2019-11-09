#!/usr/bin/env python
""" """

# Standard library modules.
import itertools
import math

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.sample.base import (
    SampleBase,
    SampleBuilderBase,
    LayeredSampleBase,
    LayeredSampleBuilderBase,
)
from pymontecarlo.options.material import Material
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


class SampleMock(SampleBase):
    def __init__(self, tilt_rad, azimuth_rad):
        super().__init__(tilt_rad, azimuth_rad)

    @property
    def materials(self):
        return []

    # region HDF5

    @classmethod
    def parse_hdf5(cls, group):
        tilt_rad = cls._parse_hdf5(group, cls.ATTR_TILT, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        return cls(tilt_rad, azimuth_rad)


# endregion


class SampleBuilderMock(SampleBuilderBase):
    def build(self):
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()

        samples = []
        for tilt_rad, azimuth_rad in itertools.product(tilts_rad, rotations_rad):
            samples.append(SampleMock(tilt_rad, azimuth_rad))
        return samples


class LayeredSampleMock(LayeredSampleBase):
    @classmethod
    def parse_hdf5(cls, group):
        tilt_rad = cls._parse_hdf5(group, cls.ATTR_TILT, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        layers = cls._parse_hdf5_layers(group)
        return cls(layers, tilt_rad, azimuth_rad)


class LayeredSampleBuilderMock(LayeredSampleBuilderBase):
    def build(self):
        layers_list = self._calculate_layer_combinations()
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()

        product = itertools.product(layers_list, tilts_rad, rotations_rad)

        samples = []
        for layers, tilt_rad, azimuth_rad in product:
            samples.append(LayeredSampleMock(layers, tilt_rad, azimuth_rad))

        return samples


@pytest.fixture
def sample():
    return SampleMock(1.1, 2.2)


@pytest.fixture
def builder():
    return SampleBuilderMock()


@pytest.fixture
def layeredbuilder():
    return LayeredSampleBuilderMock()


def test_samplebase(sample):
    assert sample.tilt_rad == pytest.approx(1.1, abs=1e-4)
    assert sample.tilt_deg == pytest.approx(math.degrees(1.1), abs=1e-4)

    assert sample.azimuth_rad == pytest.approx(2.2, abs=1e-4)
    assert sample.azimuth_deg == pytest.approx(math.degrees(2.2), abs=1e-4)

    assert len(sample.materials) == 0


def test_samplebase_eq(sample):
    assert sample == SampleMock(1.1, 2.2)
    assert sample != SampleMock(1.2, 2.2)
    assert sample != SampleMock(1.1, 2.3)


def test_samplebase_hdf5(sample, tmp_path):
    testutil.assert_convert_parse_hdf5(sample, tmp_path)


def test_samplebase_copy(sample):
    testutil.assert_copy(sample)


def test_samplebase_pickle(sample):
    testutil.assert_pickle(sample)


def test_samplebase_series(sample, seriesbuilder):
    sample.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 2


def test_samplebase_document(sample, documentbuilder):
    sample.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 5


def test_samplebuilderbase(builder):
    samples = builder.build()
    assert len(builder) == 1
    assert len(samples) == 1

    sample = samples[0]
    assert sample.tilt_rad == pytest.approx(0.0, abs=1e-4)
    assert sample.azimuth_rad == pytest.approx(0.0, abs=1e-4)


def test_samplebuilderbase_onetilt(builder):
    builder.add_tilt_rad(1.1)
    builder.add_azimuth_rad(2.2)

    samples = builder.build()
    assert len(builder) == 1
    assert len(samples) == 1

    sample = samples[0]
    assert sample.tilt_rad == pytest.approx(1.1, abs=1e-4)
    assert sample.azimuth_rad == pytest.approx(2.2, abs=1e-4)


def test_samplebuilderbase_twotilt(builder):
    builder.add_tilt_rad(1.1)
    builder.add_tilt_rad(1.1)
    builder.add_azimuth_rad(2.2)
    builder.add_azimuth_rad(2.3)

    samples = builder.build()
    assert len(builder) == 2
    assert len(samples) == 2


def test_layeredsamplebuilderbase(layeredbuilder):
    layeredbuilder = LayeredSampleBuilderMock()
    layeredbuilder.add_layer(Material.pure(29), 10)
    layeredbuilder.add_layer(Material.pure(30), 20)

    samples = layeredbuilder.build()
    assert len(layeredbuilder) == 1
    assert len(samples) == 1

    sample = samples[0]
    assert len(sample.layers) == 2


def test_layeredsamplebuilderbase_twomaterials(layeredbuilder):
    layerbuilder = layeredbuilder.add_layer(Material.pure(29), 10)
    layerbuilder.add_material(Material.pure(30))

    samples = layeredbuilder.build()
    assert len(layeredbuilder) == 2
    assert len(samples) == 2

    sample = samples[0]
    assert len(sample.layers) == 1
    assert sample.layers[0].thickness_m == pytest.approx(10.0, abs=1e-4)


def test_layeredsamplebuilderbase_twolayers(layeredbuilder):
    layerbuilder = layeredbuilder.add_layer(Material.pure(29), 10)
    layerbuilder.add_material(Material.pure(30))
    layerbuilder = layeredbuilder.add_layer(Material.pure(29), 20)
    layerbuilder.add_material(Material.pure(30))

    samples = layeredbuilder.build()
    assert len(layeredbuilder) == 4
    assert len(samples) == 4

    sample = samples[0]
    assert len(sample.layers) == 2
    assert sample.layers[0].thickness_m == pytest.approx(10.0, abs=1e-4)
    assert sample.layers[1].thickness_m == pytest.approx(20.0, abs=1e-4)

#!/usr/bin/env python
""" """

# Standard library modules.
import math

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.detector.photon import PhotonDetector, PhotonDetectorBuilder
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def detector():
    return PhotonDetector("det", math.radians(35), math.radians(90))


@pytest.fixture
def builder():
    return PhotonDetectorBuilder()


def test_photondetector(detector):
    assert detector.elevation_rad == pytest.approx(math.radians(35), abs=1e-4)
    assert detector.elevation_deg == pytest.approx(35, abs=1e-4)

    assert detector.azimuth_rad == pytest.approx(math.radians(90), abs=1e-4)
    assert detector.azimuth_deg == pytest.approx(90, abs=1e-4)


def test_photondetector_repr(detector):
    assert repr(detector) == "<PhotonDetector(det, elevation=35.0°, azimuth=90.0°)>"


def test_photondetector_eq(detector):
    assert detector == PhotonDetector("det", math.radians(35), math.radians(90))


def test_photondetector_ne(detector):
    assert not detector == PhotonDetector("det2", math.radians(35), math.radians(90))
    assert not detector == PhotonDetector(math.radians(36), math.radians(90))
    assert not detector == PhotonDetector(math.radians(35), math.radians(91))


def test_photondetector_hdf5(detector, tmp_path):
    testutil.assert_convert_parse_hdf5(detector, tmp_path)


def test_photondetector_copy(detector):
    testutil.assert_copy(detector)


def test_photondetector_pickle(detector):
    testutil.assert_pickle(detector)


def test_photondetector_series(detector, seriesbuilder):
    detector.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 2


def test_photondetector_document(detector, documentbuilder):
    detector.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 8


def test_photondetectorbuild(builder):
    builder.add_elevation_deg(1.1)
    builder.add_elevation_deg(2.2)
    builder.add_azimuth_deg(3.3)
    builder.add_azimuth_deg(4.4)

    assert len(builder) == 4
    assert len(builder.build()) == 4


def test_photondetectorbuild_noelevation(builder):
    builder.add_azimuth_deg(0.0)

    assert len(builder) == 0
    assert len(builder.build()) == 0


def test_photondetectorbuild_noazimuth(builder):
    builder.add_elevation_deg(1.1)

    assert len(builder) == 1
    assert len(builder.build()) == 1

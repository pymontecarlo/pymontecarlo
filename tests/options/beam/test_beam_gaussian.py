#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.beam.gaussian import GaussianBeam, GaussianBeamBuilder
from pymontecarlo.options.particle import Particle
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def beam():
    return GaussianBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)


@pytest.fixture
def builder():
    return GaussianBeamBuilder()


def test_gaussianbeam(beam):
    assert beam.particle == Particle.POSITRON

    assert beam.energy_eV == pytest.approx(15e3, abs=1e-4)
    assert beam.energy_keV == pytest.approx(15.0, abs=1e-4)
    assert beam.diameter_m == pytest.approx(123.456, abs=1e-4)
    assert beam.x0_m == pytest.approx(1.0, abs=1e-4)
    assert beam.y0_m == pytest.approx(2.0, abs=1e-4)


def test_gaussianbeam_repr(beam):
    assert repr(beam) == "<GaussianBeam(POSITRON, 15000 eV, 123.456 m, (1, 2) m)>"


def test_gaussianbeam_eq(beam):
    assert beam == GaussianBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)


def test_gaussianbeam_ne(beam):
    assert not beam == GaussianBeam(14e3, 123.456, Particle.POSITRON, 1.0, 2.0)
    assert not beam == GaussianBeam(15e3, 124.456, Particle.POSITRON, 1.0, 2.0)
    assert not beam == GaussianBeam(15e3, 123.456, Particle.ELECTRON, 1.0, 2.0)
    assert not beam == GaussianBeam(15e3, 123.456, Particle.POSITRON, 1.1, 2.0)
    assert not beam == GaussianBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.1)
    assert not beam == object()


def test_gaussianbeam_hdf5(beam, tmp_path):
    testutil.assert_convert_parse_hdf5(beam, tmp_path)


def test_gaussianbeam_copy(beam):
    testutil.assert_copy(beam)


def test_gaussianbeam_pickle(beam):
    testutil.assert_pickle(beam)


def test_gaussianbeam_series(beam, seriesbuilder):
    beam.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 5


def test_gaussianbeam_document(beam, documentbuilder):
    beam.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 4


def test_gaussianbeambuilder(builder):
    builder.add_energy_eV(10e3)
    builder.add_energy_keV(10)  # Not added
    builder.add_diameter_m(0.0)
    builder.add_diameter_m(0.1)
    builder.add_position(0.0, 0.0)
    builder.add_position(0.0, 0.1)

    beams = builder.build()
    assert len(beams) == 4
    assert len(builder) == 4

    for beam in beams:
        assert beam.particle == Particle.ELECTRON


def test_gaussianbeambuilder_nodiameter(builder):
    builder.add_energy_eV(10e3)
    builder.add_position(0.0, 0.0)
    builder.add_position(0.0, 0.1)
    builder.add_particle(Particle.ELECTRON)

    beams = builder.build()
    assert len(beams) == 0
    assert len(builder) == 0


def test_gaussianbeambuilder_noposition(builder):
    builder.add_energy_eV(10e3)
    builder.add_diameter_m(0.1)
    builder.add_particle(Particle.ELECTRON)

    beams = builder.build()
    assert len(beams) == 0
    assert len(builder) == 0


def test_gaussianbeambuilder_linescan(builder):
    builder.add_energy_eV(10e3)
    builder.add_diameter_m(0.123)
    builder.add_linescan_x(0.0, 5.0, 1.0, y0_m=0.456)

    beams = builder.build()
    assert len(beams) == 5
    assert len(builder) == 5

    for beam in beams:
        assert beam.particle == Particle.ELECTRON
        assert beam.diameter_m == pytest.approx(0.123, abs=1e-4)
        assert beam.y0_m == pytest.approx(0.456, abs=1e-4)

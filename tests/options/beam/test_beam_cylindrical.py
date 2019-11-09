#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.beam.cylindrical import (
    CylindricalBeam,
    CylindricalBeamBuilder,
)
from pymontecarlo.options.particle import Particle
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def beam():
    return CylindricalBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)


@pytest.fixture
def builder():
    return CylindricalBeamBuilder()


def test_cylindricalbeam(beam):
    assert beam.particle == Particle.POSITRON

    assert beam.energy_eV == pytest.approx(15e3, abs=1e-4)
    assert beam.energy_keV == pytest.approx(15.0, abs=1e-4)
    assert beam.diameter_m == pytest.approx(123.456, abs=1e-4)
    assert beam.x0_m == pytest.approx(1.0, abs=1e-4)
    assert beam.y0_m == pytest.approx(2.0, abs=1e-4)


def test_cylindricalbeam_repr(beam):
    assert repr(beam) == "<CylindricalBeam(POSITRON, 15000 eV, 123.456 m, (1, 2) m)>"


def test_cylindricalbeam_eq(beam):
    assert beam == CylindricalBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)


def test_cylindricalbeam_ne(beam):
    assert not beam == CylindricalBeam(14e3, 123.456, Particle.POSITRON, 1.0, 2.0)
    assert not beam == CylindricalBeam(15e3, 124.456, Particle.POSITRON, 1.0, 2.0)
    assert not beam == CylindricalBeam(15e3, 123.456, Particle.ELECTRON, 1.0, 2.0)
    assert not beam == CylindricalBeam(15e3, 123.456, Particle.POSITRON, 1.1, 2.0)
    assert not beam == CylindricalBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.1)
    assert not beam == object()


def test_cylindricalbeam_hdf5(beam, tmp_path):
    testutil.assert_convert_parse_hdf5(beam, tmp_path)


def test_cylindricalbeam_copy(beam):
    testutil.assert_copy(beam)


def test_cylindricalbeam_pickle(beam):
    testutil.assert_pickle(beam)


def test_cylindricalbeam_series(beam, seriesbuilder):
    beam.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 5


def test_cylindricalbeam_document(beam, documentbuilder):
    beam.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 4


def test_cylindricalbeambuilder(builder):
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


def test_cylindricalbeambuilder_nodiameter(builder):
    builder.add_energy_eV(10e3)
    builder.add_position(0.0, 0.0)
    builder.add_position(0.0, 0.1)
    builder.add_particle(Particle.ELECTRON)

    beams = builder.build()
    assert len(beams) == 0
    assert len(builder) == 0


def test_cylindricalbeambuilder_noposition(builder):
    builder.add_energy_eV(10e3)
    builder.add_diameter_m(0.1)
    builder.add_particle(Particle.ELECTRON)

    beams = builder.build()
    assert len(beams) == 0
    assert len(builder) == 0


def test_cylindricalbeambuilder_linescan(builder):
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

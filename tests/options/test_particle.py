#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.particle import Particle

# Globals and constants variables.


@pytest.mark.parametrize(
    "particle,expected", zip(Particle, ["ELECTRON", "PHOTON", "POSITRON"])
)
def test_particle_str(particle, expected):
    assert str(particle) == expected


@pytest.mark.parametrize("particle,expected", zip(Particle, [-1, 0, 1]))
def test_particle_charge(particle, expected):
    assert particle.charge == expected


@pytest.mark.parametrize(
    "particle,expected", zip(Particle, ["#00549F", "#FFD700", "#FFAB60"])
)
def test_particle_color(particle, expected):
    assert particle.color == expected

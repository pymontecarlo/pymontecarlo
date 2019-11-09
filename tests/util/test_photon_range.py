#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pyxray

import pytest

# Local modules.
from pymontecarlo.util.photon_range import photon_range
from pymontecarlo.options.material import Material

# Globals and constants variables.


def test_photon_range():
    material = Material.pure(29)
    energy_eV = pyxray.xray_transition_energy_eV(29, "Ka1", reference="jeol")

    actual = photon_range(20e3, material, 29, energy_eV)
    assert actual == pytest.approx(8.4063e-7, abs=1e-10)

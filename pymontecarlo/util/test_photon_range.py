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
    xrayline = pyxray.xray_line(29, 'Ka1')

    actual = photon_range(20e3, material, xrayline, reference='perkins1991')
    assert actual == pytest.approx(8.4063e-7, abs=1e-10)

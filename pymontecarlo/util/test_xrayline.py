#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pyxray

import pytest

# Local modules.
from pymontecarlo.util.xrayline import find_lowest_energy_known_xrayline

# Globals and constants variables.

@pytest.mark.parametrize('z,minimum_energy_eV,expected',
    [(6, 0.0, pyxray.xray_line(6, 'Ka1')),
     (13, 0.0, pyxray.xray_line(13, 'Ll')),
     (13, 1e3, pyxray.xray_line(13, 'Ka1'))
     ])
def testfind_lowest_energy_known_xrayline(z, minimum_energy_eV, expected):
    assert find_lowest_energy_known_xrayline([z], minimum_energy_eV) == expected


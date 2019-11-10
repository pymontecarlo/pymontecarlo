#!/usr/bin/env python
""" """

# Standard library modules.
import math

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.util.cbook import normalize_angle

# Globals and constants variables.


@pytest.mark.parametrize(
    "value0,value1",
    [
        (math.radians(40), math.radians(40)),
        (math.radians(320), math.radians(-40)),
        (math.radians(320), math.radians(-400)),
        (math.radians(40), math.radians(400)),
    ],
)
def test_normalize_angle(value0, value1):
    assert value0 == pytest.approx(normalize_angle(value1), 1e-4)

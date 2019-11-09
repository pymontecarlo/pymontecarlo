#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.util.electron_range import kanaya_okayama

# Globals and constants variables.


@pytest.mark.parametrize(
    "composition,expected_range",
    [({29: 1.0}, 1.45504e-6), ({29: 0.5, 30: 0.5}, 1.61829e-6)],
)
def test_kanaya_okayama(composition, expected_range):
    assert kanaya_okayama(composition, 20e3) == pytest.approx(expected_range, abs=1e-10)

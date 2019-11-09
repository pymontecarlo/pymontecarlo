#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.composition import from_formula

# Globals and constants variables.


@pytest.mark.parametrize("formula", ["Al2Na3B12", "Al 2 Na 3 B 12", "Al2 Na3 B12"])
def test_composition_from_formula(formula):
    comp = from_formula(formula)
    assert comp[13] == pytest.approx(0.21358626371988801, abs=1e-4)
    assert comp[11] == pytest.approx(0.27298103136883051, abs=1e-4)
    assert comp[5] == pytest.approx(0.51343270491128157, abs=1e-4)


def test_composition_from_formula_invalid_atomicnumber():
    with pytest.raises(Exception):
        from_formula("Aq2 Na3 B12")


def test_composition_from_formula_normalize():
    comp = from_formula("Al2")
    assert comp[13] == pytest.approx(1.0, abs=1e-4)

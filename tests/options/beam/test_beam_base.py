#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.beam.base import (
    convert_diameter_fwhm_to_sigma,
    convert_diameter_sigma_to_fwhm,
)

# Globals and constants variables.


def test_convert_diameter_fwhm_to_sigma():
    assert convert_diameter_fwhm_to_sigma(1.0) == pytest.approx(0.849321, abs=1e-4)


def test_convert_diameter_sigma_to_fwhm():
    assert convert_diameter_sigma_to_fwhm(0.849321) == pytest.approx(1.0, abs=1e-4)

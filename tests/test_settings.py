#!/usr/bin/env python
""" """

# Standard library modules.
import math

# Third party modules.
import pytest

# Local modules.
from pymontecarlo import unit_registry
from pymontecarlo.settings import XrayNotation, Settings
import pymontecarlo.util.physics as physics
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


def test_settings_hdf5(settings, tmp_path):
    settings.preferred_xray_notation = XrayNotation.SIEGBAHN
    settings.set_preferred_unit("nm")

    settings2 = testutil.assert_convert_parse_hdf5(
        settings, tmp_path, assert_equality=False
    )

    assert settings2.preferred_xray_notation == XrayNotation.SIEGBAHN
    assert (
        settings2.to_preferred_unit(1.0, unit_registry.meter).units
        == unit_registry.nanometer
    )


def test_settings_hdf5io(settings, tmp_path):
    settings.preferred_xray_notation = XrayNotation.SIEGBAHN
    settings.set_preferred_unit("nm")

    filepath = tmp_path.joinpath("settings.h5")
    settings.write(filepath)
    settings2 = Settings.read(filepath)

    assert settings2.preferred_xray_notation == XrayNotation.SIEGBAHN
    assert (
        settings2.to_preferred_unit(1.0, unit_registry.meter).units
        == unit_registry.nanometer
    )


def test_settings_set_preferred_unit(settings):
    settings.set_preferred_unit(unit_registry.lb)

    q = settings.to_preferred_unit(1.2, unit_registry.kilogram)
    assert q.magnitude == pytest.approx(2.645547, abs=1e-4)
    assert q.units == unit_registry.lb


def test_settings_set_preferred_unit_length(settings):
    settings.set_preferred_unit(unit_registry.nanometer)

    q = settings.to_preferred_unit(1.2, unit_registry.meter)
    assert q.magnitude == pytest.approx(1.2e9, abs=1e-4)
    assert q.units == unit_registry.nanometer


def test_settings_set_preferred_unit_energy(settings):
    settings.set_preferred_unit(unit_registry.joule)

    q = settings.to_preferred_unit(1.2, unit_registry.electron_volt)
    assert q.magnitude == pytest.approx(1.2 * physics.e, abs=1e-4)
    assert q.units == unit_registry.joule


def test_settings_set_preferred_unit_angle(settings):
    settings.set_preferred_unit(unit_registry.radian)

    q = settings.to_preferred_unit(1.2, unit_registry.degree)
    assert q.magnitude == pytest.approx(math.radians(1.2), abs=1e-4)
    assert q.units == unit_registry.radian


def test_settings_set_preferred_unit_density(settings):
    settings.set_preferred_unit(unit_registry.kilogram / unit_registry.meter ** 3)

    q = settings.to_preferred_unit(
        1.2, unit_registry.gram / unit_registry.centimeter ** 3
    )
    assert q.magnitude == pytest.approx(1.2e3, abs=1e-4)
    assert q.units == unit_registry.kilogram / unit_registry.meter ** 3


def test_settings_clear_preferred_units(settings):
    settings.set_preferred_unit(unit_registry.nanometer)

    q = settings.to_preferred_unit(1.2, unit_registry.meter)
    assert q.magnitude == pytest.approx(1.2e9, abs=1e-4)
    assert q.units == unit_registry.nanometer

    settings.clear_preferred_units()

    q = settings.to_preferred_unit(q)
    assert q.magnitude == pytest.approx(1.2, abs=1e-4)
    assert q.units == unit_registry.meter

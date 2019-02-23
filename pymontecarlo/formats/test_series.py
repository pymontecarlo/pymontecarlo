#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.

# Globals and constants variables.

@pytest.fixture
def seriesbuilder(seriesbuilder):
    seriesbuilder.add_column('a', 'b', 'foo')
    seriesbuilder.add_column('c', 'd', 0.2, 'm', 0.01)
    seriesbuilder.add_column('c', 'd', 6.0, 'm', error=True)
    return seriesbuilder

def test_seriesbuilder(seriesbuilder):
    seriesbuilder.abbreviate_name = False
    seriesbuilder.format_number = False

    s = seriesbuilder.build()

    assert s['a'] == 'foo'
    assert s['c [m]'] == pytest.approx(0.2, abs=1e-4)
    assert s['\u03C3(c) [m]'] == pytest.approx(6.0, abs=1e-4)

def test_seriesbuilder_abbreviate_name(seriesbuilder):
    seriesbuilder.abbreviate_name = True
    seriesbuilder.format_number = False

    s = seriesbuilder.build()

    assert s['b'] == 'foo'
    assert s['d [m]'] == pytest.approx(0.2, abs=1e-4)
    assert s['\u03C3(d) [m]'] == pytest.approx(6.0, abs=1e-4)

def test_seriesbuilder_format_number(seriesbuilder):
    seriesbuilder.abbreviate_name = False
    seriesbuilder.format_number = True

    s = seriesbuilder.build()

    assert s['a'] == 'foo'
    assert s['c [m]'] == '0.20'
    assert s['\u03C3(c) [m]'] == '6'

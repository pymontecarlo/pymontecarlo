#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pyxray

import pytest

# Local modules.
from pymontecarlo.options.xrayline import LazyLowestEnergyXrayLine
from pymontecarlo.options.material import Material
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.mark.parametrize(
    "z,beam_energy_eV,minimum_energy_eV,expected",
    [
        (6, 20e3, 0.0, pyxray.xray_line(6, "Ka1")),
        (13, 20e3, 0.0, pyxray.xray_line(13, "Ll")),
        (13, 20e3, 1e3, pyxray.xray_line(13, "Ka1")),
    ],
)
def test_lazylowestenergyxrayline(
    options, z, beam_energy_eV, minimum_energy_eV, expected
):
    options.beam.energy_eV = beam_energy_eV
    options.sample.material = Material.pure(z)

    assert LazyLowestEnergyXrayLine(minimum_energy_eV).apply(None, options) == expected


@pytest.fixture
def lazylowestenergyxrayline():
    return LazyLowestEnergyXrayLine(minimum_energy_eV=250.0)


def test_lazylowestenergyxrayline_hdf5(lazylowestenergyxrayline, tmp_path):
    testutil.assert_convert_parse_hdf5(lazylowestenergyxrayline, tmp_path)


def test_lazylowestenergyxrayline_copy(lazylowestenergyxrayline):
    testutil.assert_copy(lazylowestenergyxrayline)


def test_lazylowestenergyxrayline_pickle(lazylowestenergyxrayline):
    testutil.assert_pickle(lazylowestenergyxrayline)


def test_lazylowestenergyxrayline_series(lazylowestenergyxrayline, seriesbuilder):
    lazylowestenergyxrayline.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 0


def test_lazylowestenergyxrayline_document(lazylowestenergyxrayline, documentbuilder):
    lazylowestenergyxrayline.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 3

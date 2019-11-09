#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


def test_simulation_find_result(simulation):
    results = simulation.find_result(EmittedPhotonIntensityResult)
    assert len(results) == 1


def test_simulation_hdf5(simulation, tmp_path):
    testutil.assert_convert_parse_hdf5(simulation, tmp_path)


def test_simulation_copy(simulation):
    testutil.assert_copy(simulation)


def test_simulation_pickle(simulation):
    testutil.assert_pickle(simulation)

#!/usr/bin/env python
""" """

# Standard library modules.
import math

# Third party modules.
import pytest

from uncertainties import ufloat

# Local modules.
from pymontecarlo.mock import ProgramMock
from pymontecarlo.options.analysis.kratio import KRatioAnalysis, TAG_STANDARD
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.material import Material
from pymontecarlo.options.options import Options
from pymontecarlo.simulation import Simulation
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder
from pymontecarlo.results.kratio import KRatioResult
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def detector(options):
    return options.detectors[0]


@pytest.fixture
def analysis(detector):
    analysis = KRatioAnalysis(detector)
    analysis.add_standard_material(8, Material.from_formula("Al2O3"))
    return analysis


def test_kratioanalysis_hdf5(analysis, tmp_path):
    testutil.assert_convert_parse_hdf5(analysis, tmp_path)


def test_kratioanalysis_copy(analysis):
    testutil.assert_copy(analysis)


def test_kratioanalysis_pickle(analysis):
    testutil.assert_pickle(analysis)


def test_kratioanalysis_series(analysis, seriesbuilder):
    analysis.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 0


def test_kratioanalysis_document(analysis, documentbuilder):
    analysis.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 6


def test_kratioanalysis_apply(analysis, options):
    list_options = analysis.apply(options)
    assert len(list_options) == 1

    newoptions = list_options[0]
    assert newoptions.beam.energy_eV == pytest.approx(options.beam.energy_eV, abs=1e-4)
    assert newoptions.beam.particle == options.beam.particle
    assert isinstance(newoptions.sample, SubstrateSample)
    assert newoptions.sample.material == Material.pure(29)
    assert newoptions.detectors == options.detectors
    assert len(newoptions.analyses) == 1
    assert isinstance(newoptions.analyses[0], PhotonIntensityAnalysis)
    assert TAG_STANDARD in newoptions.tags


def test_kratioanalysis_apply_al2o3(analysis, options):
    options.sample.material = Material.from_formula("Al2O3")

    list_options = analysis.apply(options)
    assert len(list_options) == 2


def test_kratioanalysis_calculate_nothing(analysis, simulation):
    simulations = [simulation]
    newresult = analysis.calculate(simulation, simulations)
    assert not newresult


def test_kratioanalysis_calculate(analysis):
    # Create options
    program = ProgramMock()
    beam = GaussianBeam(20e3, 10.0e-9)
    sample = SubstrateSample(Material.from_formula("CaSiO4"))
    unkoptions = Options(program, beam, sample)

    list_standard_options = analysis.apply(unkoptions)
    assert len(list_standard_options) == 3

    # Create simulations
    def create_simulation(options):
        builder = EmittedPhotonIntensityResultBuilder(analysis)
        for z, wf in options.sample.material.composition.items():
            builder.add_intensity((z, "Ka"), wf * 1e3, math.sqrt(wf * 1e3))
        result = builder.build()
        return Simulation(options, [result], "sim")

    unksim = create_simulation(unkoptions)
    stdsims = [create_simulation(options) for options in list_standard_options]
    sims = stdsims + [unksim]

    # Calculate
    newresult = analysis.calculate(unksim, sims)
    assert newresult

    newresult = analysis.calculate(unksim, sims)
    assert not newresult

    # Test
    results = unksim.find_result(KRatioResult)
    assert len(results) == 1

    result = results[0]
    assert len(result) == 3

    testutil.assert_ufloats(result[("Ca", "Ka")], ufloat(0.303262, 0.019880), abs=1e-4)
    testutil.assert_ufloats(result[("Si", "Ka")], ufloat(0.212506, 0.016052), abs=1e-4)
    testutil.assert_ufloats(
        result[("O", "Ka")], ufloat(0.484232 / 0.470749, 0.066579), abs=1e-4
    )

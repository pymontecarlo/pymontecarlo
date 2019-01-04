""""""

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.runner.base import SimulationRunnerBase
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.simulation import Simulation

# Globals and constants variables.

class SimulationRunnerMock(SimulationRunnerBase):

    async def start(self):
        pass

    async def cancel(self):
        pass

    async def shutdown(self):
        pass

    def _submit(self, *list_options):
        pass

@pytest.fixture
def runner():
    return SimulationRunnerMock()

def test_prepare_simulations(runner, options):
    simulations = runner.prepare_simulations(options)
    assert len(simulations) == 1

def test_prepare_simulations_already_submitted(runner, options):
    runner.submit(options)
    simulations = runner.prepare_simulations(options)
    assert len(simulations) == 0

def test_prepare_simulations_already_in_project(runner, options):
    simulation = Simulation(options)
    simulation.results.append(object())
    runner.project.simulations.append(simulation)

    simulations = runner.prepare_simulations(options)
    assert len(simulations) == 0

def test_prepare_simulations_invalid(runner, options):
    options.beam.energy_eV = -1e3
    with pytest.raises(ValidationError) as exc:
        runner.prepare_simulations(options)
        assert len(exc.causes) == 1

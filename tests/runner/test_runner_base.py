""""""

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.runner.base import SimulationRunnerBase
from pymontecarlo.simulation import Simulation

# Globals and constants variables.


class SimulationRunnerMock(SimulationRunnerBase):
    async def start(self):
        pass

    async def cancel(self):
        pass

    async def shutdown(self):
        pass

    async def _submit(self, *list_options):
        pass


@pytest.fixture
def runner():
    return SimulationRunnerMock()


def test_prepare_simulations(runner, options):
    simulations = runner.prepare_simulations(options)
    assert len(simulations) == 1


@pytest.mark.asyncio
async def test_prepare_simulations_already_submitted(event_loop, runner, options):
    await runner.submit(options)
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
    runner.prepare_simulations(options)

#!/usr/bin/env python
""" """

# Standard library modules.
import asyncio
import copy

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.runner.local import LocalSimulationRunner
from pymontecarlo.util.token import TokenState

# Globals and constants variables.


@pytest.fixture
def runner():
    return LocalSimulationRunner(max_workers=3)


@pytest.mark.asyncio
async def test_local_runner_single_simulation(event_loop, runner, options):
    assert len(runner.project.simulations) == 0
    assert runner.token.state == TokenState.NOTSTARTED

    async with runner:
        await runner.submit(options)

    #        task = asyncio.create_task(runner.shutdown())
    #        while not task.done():
    #            await asyncio.sleep(0.5)
    #            print(runner.token.progress)

    assert len(runner.project.simulations) == 1
    assert runner.token.state == TokenState.DONE


@pytest.mark.asyncio
async def test_local_runner_multiple_simulations(event_loop, runner, options):
    options2 = copy.deepcopy(options)
    options2.beam.energy_eV = 2000

    options3 = copy.deepcopy(options)
    options3.beam.energy_eV = 3000

    async with runner:
        await runner.submit(options, options2, options3)

    assert len(runner.project.simulations) == 3
    assert runner.token.state == TokenState.DONE


@pytest.mark.asyncio
async def test_local_runner_cancel_immediately(event_loop, runner, options):
    async with runner:
        await runner.submit(options)
        await runner.cancel()

    assert len(runner.project.simulations) == 0


@pytest.mark.asyncio
async def test_local_runner_cancel(event_loop, runner, options):
    async with runner:
        await runner.submit(options)
        await asyncio.sleep(0.5)
        await runner.cancel()

    assert len(runner.project.simulations) == 0
    assert runner.token.state == TokenState.CANCELLED

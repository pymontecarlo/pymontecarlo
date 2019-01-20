#!/usr/bin/env python
""" """

# Standard library modules.
import asyncio

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
        runner.submit(options)

#        task = asyncio.create_task(runner.shutdown())
#        while not task.done():
#            await asyncio.sleep(0.5)
#            print(runner.token.progress)

    assert len(runner.project.simulations) == 1
    assert runner.token.state == TokenState.DONE

@pytest.mark.asyncio
async def test_local_runner_multiple_simulations(event_loop, runner, options):
    async with runner:
        runner.submit(options)

        options.beam.energy_eV += 1000
        runner.submit(options)

        options.beam.energy_eV += 1000
        runner.submit(options)

    assert len(runner.project.simulations) == 3
    assert runner.token.state == TokenState.DONE

@pytest.mark.asyncio
async def test_local_runner_cancel_immediately(event_loop, runner, options):
    async with runner:
        runner.submit(options)
        await runner.cancel()

    assert len(runner.project.simulations) == 0

@pytest.mark.asyncio
async def test_local_runner_cancel(event_loop, runner, options):
    async with runner:
        runner.submit(options)
        await asyncio.sleep(0.5)
        await runner.cancel()

    assert len(runner.project.simulations) == 0
    assert runner.token.state == TokenState.CANCELLED

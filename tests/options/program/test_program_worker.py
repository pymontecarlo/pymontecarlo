#!/usr/bin/env python
""" """

# Standard library modules.
import asyncio

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.mock import WorkerMock
from pymontecarlo.simulation import Simulation
from pymontecarlo.util.token import Token, TokenState
from pymontecarlo.exceptions import ExportError

# Globals and constants variables.


@pytest.mark.asyncio
async def testrun(event_loop, options, tmpdir):
    worker = WorkerMock()
    token = Token("test")
    simulation = Simulation(options)

    await worker.run(token, simulation, tmpdir)

    assert token.state == TokenState.DONE
    assert token.progress == 1.0
    assert token.status == "Done"
    assert len(simulation.results) == 1


@pytest.mark.asyncio
async def testrun_cancel(event_loop, options, tmpdir):
    worker = WorkerMock()
    token = Token("test")
    simulation = Simulation(options)

    task = asyncio.create_task(worker.run(token, simulation, tmpdir))

    await asyncio.sleep(0.5)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        assert True, "Task was cancelled properly"
    else:
        assert False

    assert token.state == TokenState.CANCELLED


@pytest.mark.asyncio
async def testrun_error(event_loop, options, tmpdir):
    options.beam.energy_eV = 0.0  # To cause WorkerErrorr

    worker = WorkerMock()
    token = Token("test")
    simulation = Simulation(options)

    try:
        await worker.run(token, simulation, tmpdir)
    except ExportError:
        assert True
    else:
        assert False

    assert token.state == TokenState.ERROR

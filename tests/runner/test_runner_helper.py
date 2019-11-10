""""""

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.runner.helper import run_async

# Globals and constants variables.


@pytest.mark.asyncio
async def test_run_async(event_loop, options):
    project = await run_async([options], progress=True)

    assert len(project.simulations) == 1

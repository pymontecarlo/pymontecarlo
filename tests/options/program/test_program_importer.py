#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.mock import ImporterMock

# Globals and constants variables.

@pytest.fixture
def importer():
    return ImporterMock()

@pytest.mark.asyncio
async def test_import_(event_loop, importer, options, tmp_path):
    results = await importer.import_(options, tmp_path)

    assert len(results) == 1


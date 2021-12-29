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

    result = results[0]
    assert len(result) == 6
    assert result[(29, "Ka1")].n == pytest.approx(100.0, abs=1e-4)
    assert result[(29, "Ka")].n == pytest.approx(100.0, abs=1e-4)
    assert result[(29, "K")].n == pytest.approx(100.0, abs=1e-4)
    assert result[(29, "La1")].n == pytest.approx(100.0, abs=1e-4)
    assert result[(29, "La")].n == pytest.approx(100.0, abs=1e-4)
    assert result[(29, "L")].n == pytest.approx(100.0, abs=1e-4)

""""""

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.mock import ProgramMock
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def program():
    return ProgramMock()


def test_program_hdf5(program, tmp_path):
    testutil.assert_convert_parse_hdf5(program, tmp_path)


def test_program_copy(program):
    testutil.assert_copy(program)


def test_program_pickle(program):
    testutil.assert_pickle(program)


def test_program_series(program, seriesbuilder):
    program.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 3


def test_program_document(program, documentbuilder):
    program.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 6

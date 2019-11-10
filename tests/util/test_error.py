""""""

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.util.error import ErrorAccumulator
from pymontecarlo.exceptions import AccumulatedError, AccumulatedWarning

# Globals and constants variables.


def test_exception_only():
    with pytest.raises(AccumulatedError) as exception:
        with ErrorAccumulator() as erracc:
            erracc.add_exception(ValueError("test"))

        assert len(exception.causes) == 1


def test_warning_only():
    with pytest.warns(AccumulatedWarning) as warning:
        with ErrorAccumulator() as erracc:
            erracc.add_warning(RuntimeWarning("test"))

        assert len(warning) == 1


def test_exception_and_warning():
    with pytest.raises(AccumulatedError) as exception:
        with pytest.warns(AccumulatedWarning) as warning:
            with ErrorAccumulator() as erracc:
                erracc.add_warning(RuntimeWarning("test"))
                erracc.add_exception(ValueError("test"))

            assert len(warning) == 1

        assert len(exception.causes) == 1


def test_exception_in_context():
    with pytest.raises(AccumulatedError) as exception:
        with ErrorAccumulator() as erracc:
            erracc.add_exception(ValueError("test"))
            raise ValueError("test2")

        assert len(exception.causes) == 2

""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.parameter import ParameterType, SimpleParameter

# Globals and constants variables.


class Object:
    def __init__(self):
        self.value = 10


@pytest.fixture
def parameter():
    return SimpleParameter(
        "simple",
        lambda obj: obj.value,
        lambda obj, value: setattr(obj, "value", value),
        minimum_value=0.0,
        maximum_value=10.0,
    )


def test_simpleparameter_name(parameter):
    assert parameter.name == "simple"


def test_simpleparameter_get_value(parameter):
    obj = Object()
    assert parameter.get_value(obj) == pytest.approx(10.0, abs=1e-4)


@pytest.mark.parametrize("value,expected_value", [(5, 5), (-5, 0), (15, 10)])
def test_simpleparameter_set_value(parameter, value, expected_value):
    obj = Object()
    parameter.type_ = ParameterType.UNKNOWN
    parameter.set_value(obj, value)

    assert parameter.get_value(obj) == pytest.approx(expected_value, abs=1e-4)
    assert obj.value == pytest.approx(expected_value, abs=1e-4)


@pytest.mark.parametrize("type_", [ParameterType.FIXED, ParameterType.DIFFERENCE])
def test_simpleparameter_set_value_invalid_type(parameter, type_):
    obj = Object()
    parameter.type_ = type_

    with pytest.raises(ValueError):
        parameter.set_value(obj, 5)

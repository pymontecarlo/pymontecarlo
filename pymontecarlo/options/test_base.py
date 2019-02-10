""""""

# Standard library modules.

# Third party modules.

# Local modules.
import pymontecarlo.options.base as base

# Globals and constants variables.

class LazyOptionValueMock(base.LazyOptionValueBase):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return super().__eq__(other) and base.isclose(self.value, other.value)

    def apply(self, option, options):
        return self.value

def test_isclose_numbers():
    assert base.isclose(4.0, 4.01, abs_tol=0.1)

def test_isclose_none():
    assert base.isclose(None, None)
    assert not base.isclose(None, 4.0)
    assert not base.isclose(4.0, None)

def test_isclose_lazy():
    value0 = LazyOptionValueMock(1)

    assert base.isclose(value0, LazyOptionValueMock(1))
    assert not base.isclose(value0, LazyOptionValueMock(2))
    assert not base.isclose(value0, None)
    assert not base.isclose(value0, 1)

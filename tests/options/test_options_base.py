""""""

# Standard library modules.

# Third party modules.

# Local modules.
import pymontecarlo.options.base as base

# Globals and constants variables.


class LazyOptionMock(base.LazyOptionBase):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return super().__eq__(other) and base.isclose(self.value, other.value)

    def apply(self, option, options):
        return self.value

    # region HDF5

    ATTR_VALUE = "value"

    @classmethod
    def parse_hdf5(cls, group):
        value = cls._parse_hdf5(group, cls.ATTR_VALUE, float)
        return cls(value)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_VALUE, self.value)


def test_isclose_numbers():
    assert base.isclose(4.0, 4.01, abs_tol=0.1)


def test_isclose_none():
    assert base.isclose(None, None)
    assert not base.isclose(None, 4.0)
    assert not base.isclose(4.0, None)


def test_isclose_lazy():
    value0 = LazyOptionMock(1)

    assert base.isclose(value0, LazyOptionMock(1))
    assert not base.isclose(value0, LazyOptionMock(2))
    assert not base.isclose(value0, None)
    assert not base.isclose(value0, 1)

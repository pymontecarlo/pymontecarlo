"""
Base option class
"""

# Standard library modules.
import abc
import math
import numbers

# Third party modules.

# Local modules.
from pymontecarlo.entity import (
    EntityBase,
    EntityHDF5Mixin,
    EntitySeriesMixin,
    EntityDocumentMixin,
)
from pymontecarlo.formats.base import LazyFormat

# Globals and constants variables.


class OptionBase(EntityBase, EntityHDF5Mixin, EntitySeriesMixin, EntityDocumentMixin):
    """
    Base class of all the options.
    All derived classes should implement

        - method :meth:`__eq__`
    """

    @abc.abstractmethod
    def __eq__(self, other):
        """
        Returns whether two options are equal.
        Each option should implement some tolerance for the comparison of
        float values.
        """
        return type(other) == type(self)


class LazyOptionBase(OptionBase, LazyFormat):
    def __eq__(self, other):
        """
        Returns whether two lazy options are equal.
        """
        return type(other) == type(self)

    @abc.abstractmethod
    def apply(self, parent_option, options):
        raise NotImplementedError

    def format(self, settings):
        return "auto"

    @classmethod
    def parse_hdf5(cls, group):
        return cls()

    def convert_hdf5(self, group):
        super().convert_hdf5(group)

    def convert_series(self, builder):
        super().convert_series(builder)

    def convert_document(self, builder):
        super().convert_document(builder)


class OptionBuilderBase(metaclass=abc.ABCMeta):
    """
    Base class of all option builders.
    All derived classes should implement

        - method :meth:`__len__`
        - method :meth:`build()`
    """

    @abc.abstractmethod
    def __len__(self):
        """
        Returns the number of options that would be returned by :meth:`build()`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def build(self):
        """
        Returns a list of options.
        """
        raise NotImplementedError


class LazyMultiplierDecorator(LazyOptionBase):
    def __init__(self, lazyoption, multiplier):
        self.lazyoption = lazyoption
        self.multiplier = multiplier

    def __eq__(self, other):
        """
        Returns whether two lazy options are equal.
        """
        return (
            super().__eq__(other)
            and self.lazyoption == other.lazyoption
            and self.multiplier == other.multiplier
        )

    def apply(self, parent_option, options):
        return self.lazyoption.apply(parent_option, options) * self.multiplier

    @classmethod
    def parse_hdf5(cls, group):
        raise NotImplementedError

    def convert_hdf5(self, group):
        raise NotImplementedError

    def convert_series(self, builder):
        return self.lazyoption.convert_series(builder)

    def convert_document(self, builder):
        return self.lazyoption.convert_document(builder)


class MultiplierAttribute(object):
    def __init__(self, attrname, multiplier):
        self.attrname = attrname
        self.multiplier = multiplier

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        value = getattr(instance, self.attrname)

        if isinstance(value, LazyOptionBase):
            return LazyMultiplierDecorator(value, self.multiplier)

        return value * self.multiplier

    def __set__(self, instance, value):
        setattr(instance, self.attrname, value / self.multiplier)

    def __delete__(self, instance):
        delattr(instance, self.attrname)


class DegreesAttribute(MultiplierAttribute):
    def __init__(self, attrname_rad):
        super().__init__(attrname_rad, 180.0 / math.pi)


def apply_lazy(option, parent_option, options):
    if isinstance(option, LazyOptionBase):
        return option.apply(parent_option, options)
    else:
        return option


def isclose(value0, value1, rel_tol=1e-9, abs_tol=0.0):
    """
    Same as :func:`math.isclose`, except that function checks for lazy option values.
    """
    if isinstance(value0, LazyOptionBase):
        return value0 == value1
    elif isinstance(value0, numbers.Number) and isinstance(value1, numbers.Number):
        return math.isclose(value0, value1, rel_tol=rel_tol, abs_tol=abs_tol)
    else:
        return value0 == value1


def are_sequence_equal(list0, list1):
    if isinstance(list0, LazyOptionBase) and list0 != list1:
        return False

    if len(list0) != len(list1):
        return False

    for item0, item1 in zip(list0, list1):
        if item0 != item1:
            return False

    return True


def are_sequence_similar(list0, list1):
    if isinstance(list0, LazyOptionBase) and list0 != list1:
        return False

    if len(list0) != len(list1):
        return False

    for item0 in list0:
        count = sum(item0 == item1 for item1 in list1)
        if count != 1:
            return False

    return True


def are_sequence_close(list0, list1, rel_tol=1e-9, abs_tol=0.0):
    if isinstance(list0, LazyOptionBase) and list0 != list1:
        return False

    if len(list0) != len(list1):
        return False

    for item0, item1 in zip(list0, list1):
        if not isclose(item0, item1, rel_tol=rel_tol, abs_tol=abs_tol):
            return False

    return True


def are_mapping_equal(map0, map1):
    if isinstance(map0, LazyOptionBase) and map0 != map1:
        return False

    if len(map0) != len(map1):
        return False

    for key in map0:
        if key not in map1:
            return False

        if map0[key] != map1[key]:
            return False

    return True


def are_mapping_value_close(map0, map1, rel_tol=1e-9, abs_tol=0.0):
    if isinstance(map0, LazyOptionBase) and map0 != map1:
        return False

    if len(map0) != len(map1):
        return False

    for key in map0:
        if key not in map1:
            return False

        value0 = map0[key]
        value1 = map1[key]

        if not isclose(value0, value1, rel_tol=rel_tol, abs_tol=abs_tol):
            return False

    return True

""""""

# Standard library modules.
import abc
import math

# Third party modules.
import pandas as pd

# Local modules.
import pymontecarlo
from pymontecarlo.exceptions import ConvertError
from pymontecarlo.util.entrypoint import resolve_entrypoints
from pymontecarlo.util.tolerance import tolerance_to_decimals

# Globals and constants variables.
ENTRYPOINT_SERIESHANDLER = 'pymontecarlo.formats.series'

def find_convert_serieshandler(obj):
    for clasz in resolve_entrypoints(ENTRYPOINT_SERIESHANDLER):
        handler = clasz()
        if handler.can_convert(obj):
            return handler
    raise ConvertError("No handler found for object {!r}".format(obj))

class SeriesColumn:

    def __init__(self, name, abbrev, unit=None, tolerance=None):
        self._name = name
        self._abbrev = abbrev
        self._unit = unit
        self._tolerance = tolerance

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return type(self) == type(other) and self.name == other.name

    def __hash__(self):
        # NOTE: To allow slicing of series using only name
        return hash(self.name)

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

    def compare(self, value0, value1):
        if self.tolerance is None:
            return value0 == value1
        else:
            return math.isclose(value0, value1, abs_tol=self.tolerance)

    def with_prefix(self, prefix, prefix_abbrev=None):
        """
        Returns a new column with the prepended prefix.
        """
        if prefix_abbrev is None:
            prefix_abbrev = prefix

        name = prefix + self.name
        abbrev = prefix_abbrev + self.abbrev
        return self.__class__(name, abbrev, self.unit, self.tolerance)

    def format_value(self, value):
        if self.unit:
            q = pymontecarlo.unit_registry.Quantity(value, self.unit)
            q = pymontecarlo.settings.to_preferred_unit(q)
            value = q.magnitude

        if isinstance(value, float):
            if self.tolerance:
                if self.unit:
                    q_tolerance = pymontecarlo.unit_registry.Quantity(self.tolerance, self.unit)
                    q_tolerance = pymontecarlo.settings.to_preferred_unit(q_tolerance)
                    tolerance = q_tolerance.magnitude
                else:
                    tolerance = self.tolerance

                precision = tolerance_to_decimals(tolerance)
                return '{0:.{precision}f}'.format(value, precision=precision)
            else:
                return '{:g}'.format(value)
        else:
            return '{}'.format(value)

    @property
    def name(self):
        return self._name

    @property
    def fullname(self):
        if not self.unit:
            return self.name

        q = pymontecarlo.unit_registry.Quantity(1.0, self.unit)
        q = pymontecarlo.settings.to_preferred_unit(q)
        unitname = '{0:~P}'.format(q.units)
        if not unitname: # required for radian and degree
            unitname = '{0:P}'.format(q.units)

        return '{} ({})'.format(self.name, unitname)

    @property
    def abbrev(self):
        return self._abbrev

    @property
    def unit(self):
        return self._unit

    @property
    def tolerance(self):
        return self._tolerance

def update_with_prefix(s, prefix, prefix_abbrev=None):
    s_new = pd.Series()

    for column, value in s.items():
        column_new = column.with_prefix(prefix, prefix_abbrev)
        s_new[column_new] = value

    return s_new

class SeriesHandler(object, metaclass=abc.ABCMeta):

    def _find_and_convert(self, obj, prefix=None, prefix_abbrev=None):
        s = find_convert_serieshandler(obj).convert(obj)

        if prefix:
            s = update_with_prefix(s, prefix, prefix_abbrev)

        return s

    def can_convert(self, obj):
        return type(obj) is self.CLASS

    @abc.abstractmethod
    def convert(self, obj):
        return pd.Series()

    @abc.abstractproperty
    def CLASS(self):
        raise NotImplementedError

    @property
    def VERSION(self):
        return 1

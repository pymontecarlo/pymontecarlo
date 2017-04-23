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
from pymontecarlo.util.cbook import get_valid_filename

# Globals and constants variables.
ENTRYPOINT_SERIESHANDLER = 'pymontecarlo.formats.series'

def find_convert_serieshandler(obj):
    for clasz in resolve_entrypoints(ENTRYPOINT_SERIESHANDLER):
        handler = clasz()
        if handler.can_convert(obj):
            return handler
    raise ConvertError("No handler found for object {!r}".format(obj))

def create_identifier(series):
    try:
        preferred_units = list(pymontecarlo.settings.preferred_units.values())
        pymontecarlo.settings.clear_preferred_units(quiet=True)
        pymontecarlo.settings.set_preferred_unit('nm', quiet=True)
        pymontecarlo.settings.set_preferred_unit('deg', quiet=True)
        pymontecarlo.settings.set_preferred_unit('keV', quiet=True)
        pymontecarlo.settings.set_preferred_unit('g/cm^3', quiet=True)

        items = []
        for column, value in series.iteritems():
            key = column.abbrev
            value = column.format_value(value, tolerance=None)
            unitname = column.unitname
            items.append('{}_{}{}'.format(key, value, unitname))
    finally:
        for units in preferred_units:
            pymontecarlo.settings.set_preferred_unit(units, quiet=True)

    return get_valid_filename('_'.join(items))

def update_with_prefix(s, prefix, prefix_abbrev=None):
    s_new = pd.Series()

    for column, value in s.items():
        column_new = PrefixSeriesColumn(column, prefix, prefix_abbrev)
        s_new[column_new] = value

    return s_new

class SeriesColumn(metaclass=abc.ABCMeta):

    _default = object()

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

    def format_value(self, value, unit=_default, tolerance=_default):
        if tolerance is self._default:
            tolerance = self.tolerance
        if unit is self._default:
            unit = self.unit

        if unit is not None:
            q = pymontecarlo.unit_registry.Quantity(value, unit)
            q = pymontecarlo.settings.to_preferred_unit(q)
            value = q.magnitude

        if isinstance(value, float):
            if tolerance is not None:
                if unit is not None:
                    q_tolerance = pymontecarlo.unit_registry.Quantity(tolerance, unit)
                    q_tolerance = pymontecarlo.settings.to_preferred_unit(q_tolerance)
                    tolerance = q_tolerance.magnitude

                precision = tolerance_to_decimals(tolerance)
                return '{0:.{precision}f}'.format(value, precision=precision)
            else:
                return '{:g}'.format(value)
        else:
            return '{}'.format(value)

    def convert_value(self, value, unit=_default):
        if unit is self._default:
            unit = self.unit

        if unit is not None:
            q = pymontecarlo.unit_registry.Quantity(value, unit)
            q = pymontecarlo.settings.to_preferred_unit(q)
            value = q.magnitude

        return value

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError

    @property
    def fullname(self):
        if self.unit is None:
            return self.name

        q = pymontecarlo.unit_registry.Quantity(1.0, self.unit)
        q = pymontecarlo.settings.to_preferred_unit(q)
        unitname = '{0:~P}'.format(q.units)
        if not unitname: # required for radian and degree
            unitname = '{0:P}'.format(q.units)

        return '{} [{}]'.format(self.name, unitname)

    @abc.abstractproperty
    def abbrev(self):
        raise NotImplementedError

    @abc.abstractproperty
    def unit(self):
        raise NotImplementedError

    @property
    def unitname(self):
        if self.unit is None:
            return ''

        q = pymontecarlo.unit_registry.Quantity(1.0, self.unit)
        q = pymontecarlo.settings.to_preferred_unit(q)
        unitname = '{0:~P}'.format(q.units)
        if not unitname: # required for radian and degree
            unitname = '{0:P}'.format(q.units)

        return unitname

    @abc.abstractproperty
    def tolerance(self):
        raise NotImplementedError

class NamedSeriesColumn(SeriesColumn):

    def __init__(self, name, abbrev, unit=None, tolerance=None):
        super().__init__()
        self._name = name
        self._abbrev = abbrev
        self._unit = unit
        self._tolerance = tolerance

    @property
    def name(self):
        return self._name

    @property
    def abbrev(self):
        return self._abbrev

    @property
    def unit(self):
        return self._unit

    @property
    def tolerance(self):
        return self._tolerance

class _ParentSeriesColumn(SeriesColumn):

    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    def __hash__(self):
        return hash(self.parent)

    @property
    def name(self):
        return self.parent.name

    @property
    def abbrev(self):
        return self.parent.abbrev

    @property
    def unit(self):
        return self.parent.unit

    @property
    def tolerance(self):
        return self.parent.tolerance

    @property
    def parent(self):
        return self._parent

class PrefixSeriesColumn(_ParentSeriesColumn):

    def __init__(self, parent, prefix, prefix_abbrev=None):
        super().__init__(parent)
        self._prefix = prefix
        self._prefix_abbrev = prefix_abbrev or prefix

    def __hash__(self):
        return hash((self._prefix, self.parent))

    @property
    def name(self):
        return self._prefix + super().name

    @property
    def abbrev(self):
        return self._prefix_abbrev + super().abbrev

class ErrorSeriesColumn(_ParentSeriesColumn):

    def __init__(self, parent):
        super().__init__(parent)

    def __hash__(self):
        return hash(('error', self.parent))

    @property
    def name(self):
        return '\u03C3({})'.format(super().name)

    @property
    def abbrev(self):
        return '\u03C3({})'.format(super().abbrev)

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

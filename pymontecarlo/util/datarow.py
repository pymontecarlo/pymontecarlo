""""""

# Standard library modules.
import abc
import collections
from collections import OrderedDict
import math

# Third party modules.

# Local modules.
import pymontecarlo

# Globals and constants variables.

class DataRowCreator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_datarow(self, **kwargs):
        return DataRow()

class DataRow(collections.Mapping):

    _QUANTITY_NAN = pymontecarlo.unit_registry.Quantity(float('nan')).plus_minus(0.0)
    _UNITS_NONE = pymontecarlo.unit_registry.parse_units('')

    def __init__(self):
        self._values = OrderedDict()

    def __repr__(self):
        items = ', '.join('{0}: {1}'.format(column, self[column])
                          for column in self.columns)
        return '<{classname}({items})>'.format(classname=self.__class__.__name__,
                                               items=items)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __getitem__(self, column):
        return self._values[column][0]

    def __or__(self, other):
        outdatarow = self.__class__()
        for datarow in [self, other]:
            outdatarow.update(datarow)
        return outdatarow

    def __ior__(self, other):
        self.update(other)
        return self

    def __xor__(self, other):
        columns_all = set()
        columns_all.update(self.keys())
        columns_all.update(other.keys())

        columns_diff = set()
        for column in columns_all:
            q_self = self.get(column)
            if q_self is None:
                columns_diff.add(column)
                continue

            q_other = other.get(column)
            if q_other is None:
                columns_diff.add(column)
                continue

            q_self = q_self.to_base_units()
            q_other = q_other.to_base_units()
            q_tol = self._values[column][1]
            tolerance = q_tol.to_base_units().magnitude

            if not math.isclose(q_self.n, q_other.n, abs_tol=tolerance):
                columns_diff.add(column)
                continue

            if not math.isclose(q_self.s, q_other.s, abs_tol=tolerance):
                columns_diff.add(column)
                continue

        outdatarow = self.__class__()

        for datarow in [self, other]:
            for column, (q, q_tol) in datarow._values.items():
                if column not in columns_diff:
                    continue
                if column in outdatarow:
                    continue
                tolerance = q_tol.to(q.units).magnitude
                outdatarow.add(column, q.n, q.s, q.units, tolerance)

        return outdatarow

    def add(self, column, value, error=0.0, unit=None, tolerance=1e-13):
        if unit is None:
            unit = self._UNITS_NONE

        if isinstance(unit, str):
            unit = pymontecarlo.unit_registry.parse_units(unit)

        q = pymontecarlo.unit_registry.Quantity(value, unit)
        q = q.plus_minus(error)

        q_tol = pymontecarlo.unit_registry.Quantity(tolerance, unit)

        self._values[column] = (q, q_tol)

    def update(self, other):
        self.update_with_prefix('', other)

    def update_with_prefix(self, prefix, other):
        for column, (q, q_tol) in other._values.items():
            tolerance = q_tol.to(q.units).magnitude
            self.add(prefix + column, q.n, q.s, q.units, tolerance)

    def to_list(self, columns=None):
        if columns is None:
            columns = self.columns

        outlist = []
        for column in columns:
            columnname = str(column)
            columnname_e = '\u03C3(' + str(column) + ')'

            # Get value
            q = self.get(column, self._QUANTITY_NAN)

            # Convert to preferred unit
            q = pymontecarlo.settings.to_preferred_unit(q)

            # Unit string
            if q.units != self._UNITS_NONE:
                unitname = '{0:~P}'.format(q.units)
                if not unitname: # required for radian and degree
                    unitname = '{0:P}'.format(q.units)

                columnname += ' (' + unitname + ')'
                columnname_e += ' (' + unitname + ')'

            # Add to list
            outlist.append((columnname, q.value.magnitude))

            # Add error to list if not equal to 0.0
            if q.error.magnitude:
                outlist.append((columnname_e, q.error.magnitude))

        return outlist

    @property
    def columns(self):
        return tuple(self._values.keys())

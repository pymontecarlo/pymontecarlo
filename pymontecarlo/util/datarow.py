""""""

# Standard library modules.
import collections
from collections import OrderedDict
import numbers

# Third party modules.

# Local modules.
import pymontecarlo.util.units as units

# Globals and constants variables.

class DataRow(collections.Mapping):

    _QUANTITY_NAN = units.ureg.Quantity(float('nan')).plus_minus(0.0)
    _UNITS_NONE = units.ureg.parse_units('')

    def __init__(self):
        self._items = OrderedDict()

    def __repr__(self):
        items = ', '.join('{0}: {1}'.format(column, self[column])
                          for column in self.columns)
        return '<{classname}({items})>'.format(classname=self.__class__.__name__,
                                               items=items)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, column):
        return self._items[column]

    def __or__(self, other):
        outdatarow = self.__class__()
        for datarow in [self, other]:
            outdatarow.update(datarow)
        return outdatarow

    def __ior__(self, other):
        self.update(other)
        return self

    def __xor__(self, other):
        items_diff = set()
        items_diff ^= set(self.items())
        items_diff ^= set(other.items())
        items_diff = dict(items_diff)

        outdatarow = self.__class__()

        for datarow in [self, other]:
            for column, (value, error, unit) in datarow.items():
                if column not in items_diff:
                    continue
                if column in outdatarow:
                    continue
                outdatarow.add(column, value, error, unit)

        return outdatarow

    def add(self, column, value, error=0.0, unit=None):
        if unit is None:
            unit = self._UNITS_NONE
        if isinstance(unit, str):
            unit = units.ureg.parse_units(unit)
        self._items[column] = (value, error, unit)

    def update(self, other):
        self.update_with_prefix('', other)

    def update_with_prefix(self, prefix, other):
        for column, (value, error, unit) in other.items():
            self.add(prefix + column, value, error, unit)

    def to_list(self, columns=None):
        if columns is None:
            columns = self.columns

        outlist = []
        for column in columns:
            columnname = str(column)
            columnname_e = '\u03C3(' + str(column) + ')'

            # Get value
            value, error, unit = self.get(column, (float('nan'), 0.0, None))

            if not isinstance(value, numbers.Number):
                outlist.append((columnname, value))
                continue

            # Convert to quantity and preferred unit
            q = units.ureg.Quantity(value, unit)
            q = q.plus_minus(error)
            q = units.to_preferred_unit(q)

            # Unit string
            if q.units != self._UNITS_NONE:
                unitname = '{0:~P}'.format(q.units)
                if not unitname: # required for radian and degree
                    unitname = '{0:P}'.format(q.units)

                columnname += ' (' + unitname + ')'
                columnname_e += ' (' + unitname + ')'

            outlist.append((columnname, q.value.magnitude))
            if q.error.magnitude:
                outlist.append((columnname_e, q.error.magnitude))

        return outlist

    @property
    def columns(self):
        return tuple(self._items.keys())

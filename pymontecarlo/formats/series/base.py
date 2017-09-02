""""""

# Standard library modules.
import abc
import math

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.exceptions import ConvertError
from pymontecarlo.settings import Settings
from pymontecarlo.util.entrypoint import resolve_entrypoints, ENTRYPOINT_SERIESHANDLER
from pymontecarlo.util.tolerance import tolerance_to_decimals
from pymontecarlo.util.cbook import get_valid_filename

# Globals and constants variables.

def find_convert_serieshandler(obj, settings):
    for entrypoint in resolve_entrypoints(ENTRYPOINT_SERIESHANDLER).values():
        clasz = entrypoint.resolve()
        handler = clasz(settings)
        if handler.can_convert(obj):
            return handler
    raise ConvertError("No handler found for object {!r}".format(obj))

def create_identifiers(objs):
    settings = Settings()
    settings.set_preferred_unit('nm')
    settings.set_preferred_unit('deg')
    settings.set_preferred_unit('keV')
    settings.set_preferred_unit('g/cm^3')

    list_series = []

    for obj in objs:
        handler = find_convert_serieshandler(obj, settings)
        s = handler.convert(obj, abbreviate_name=True, format_number=True)
        list_series.append(s)

    df = pd.DataFrame(list_series)
    df = ensure_distinc_columns(df)

    identifiers = []
    for _, s in df.iterrows():
        items = ['{}={}'.format(key, value) for key, value in s.iteritems()]
        identifier = get_valid_filename('_'.join(items))
        identifiers.append(identifier)

    return identifiers

def create_identifier(obj):
    return create_identifiers([obj])[0]

def ensure_distinc_columns(dataframe, tolerances=None):
    if len(dataframe) < 2:
        return dataframe

    if tolerances is None:
        tolerances = {}

    drop_columns = []
    for column in dataframe.columns:
        values = dataframe[column].values
        tolerance = tolerances.get(column)

        if tolerance is None:
            allequal = all(values[0] == v for v in values)
        else:
            allequal = all(math.isclose(values[0], v, abs_tol=tolerance) for v in values)

        if allequal:
            drop_columns.append(column)

    return dataframe.drop(drop_columns, axis=1)

class SeriesBuilder:

    def __init__(self, settings):
        self.settings = settings
        self.data = []

    def _format_name(self, name, unit, error):
        if error:
            fmt = '\u03C3({name})'
        else:
            fmt = '{name}'

        if unit is not None:
            fmt += ' [{unitname}]'

        if callable(name):
            name = name(self.settings)

        unitname = self._format_unit(unit)

        return fmt.format(name=name, unitname=unitname)

    def _format_abbrev(self, abbrev, unit, error):
        if error:
            fmt = '\u03C3({abbrev})'
        else:
            fmt = '{abbrev}'

        if unit is not None:
            fmt += '[{unitname}]'

        if callable(abbrev):
            abbrev = abbrev(self.settings)

        unitname = self._format_unit(unit)

        return fmt.format(abbrev=abbrev, unitname=unitname)

    def _format_unit(self, unit):
        if unit is None:
            return ''

        q = self.settings.to_preferred_unit(1.0, unit)
        unitname = '{0:~P}'.format(q.units)
        if not unitname: # required for radian and degree
            unitname = '{0:P}'.format(q.units)

        return unitname

    def _format_value(self, value, unit, tolerance):
        value = self._convert_value(value, unit)

        if isinstance(value, float):
            if tolerance is not None:
                if unit is not None:
                    q_tolerance = self.settings.to_preferred_unit(tolerance, unit)
                    tolerance = q_tolerance.magnitude

                precision = tolerance_to_decimals(tolerance)
                return '{0:.{precision}f}'.format(value, precision=precision)
            else:
                return '{:g}'.format(value)
        else:
            return '{}'.format(value)

    def _convert_value(self, value, unit):
        if unit is not None:
            q = self.settings.to_preferred_unit(value, unit)
            value = q.magnitude
        return value

    def add_column(self, name, abbrev, value, unit=None, tolerance=None, error=False):
        datum = {'name': name,
                 'abbrev': abbrev,
                 'value': value,
                 'unit': unit,
                 'tolerance': tolerance,
                 'error': error}
        self.data.append(datum)

    def add_object(self, obj, prefix='', prefix_abbrev=''):
        handler = find_convert_serieshandler(obj, self.settings)
        other = handler._convert(obj)

        prefix_abbrev = prefix_abbrev or prefix

        for datum in other.data:
            datum = datum.copy()
            datum['prefix'] = datum.get('prefix', '') + prefix
            datum['prefix_abbrev'] = datum.get('prefix_abbrev', '') + prefix_abbrev
            self.data.append(datum)

    def build(self, abbreviate_name=False, format_number=False, return_tolerances=False):
        s = pd.Series()
        tolerances = {}

        for datum in self.data:
            value = datum['value']
            unit = datum['unit']
            error = datum['error']
            tolerance = datum['tolerance']

            if abbreviate_name:
                abbrev = datum['abbrev']
                prefix_abbrev = datum.get('prefix_abbrev', '')
                key = prefix_abbrev + self._format_abbrev(abbrev, unit, error)
            else:
                name = datum['name']
                prefix = datum.get('prefix', '')
                key = prefix + self._format_name(name, unit, error)

            if format_number:
                value = self._format_value(value, unit, tolerance)
            else:
                value = self._convert_value(value, unit)

            s[key] = value

            if tolerance is not None:
                tolerances[key] = self._convert_value(tolerance, unit)

        if return_tolerances:
            return s, tolerances

        return s

class SeriesHandler(object, metaclass=abc.ABCMeta):

    def __init__(self, settings):
        self.settings = settings

    def can_convert(self, obj):
        return type(obj) is self.CLASS

    def convert(self, obj, abbreviate_name=False, format_number=False, return_tolerances=False):
        return self._convert(obj).build(abbreviate_name, format_number, return_tolerances)

    @abc.abstractmethod
    def _convert(self, obj):
        return SeriesBuilder(self.settings)

    @abc.abstractproperty
    def CLASS(self):
        raise NotImplementedError

    @property
    def VERSION(self):
        return 1

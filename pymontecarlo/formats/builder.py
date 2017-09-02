""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.util.tolerance import tolerance_to_decimals

# Globals and constants variables.

class FormatBuilder(object, metaclass=abc.ABCMeta):

    def __init__(self, settings, abbreviate_name=False, format_number=False):
        self.settings = settings
        self.abbreviate_name = abbreviate_name
        self.format_number = format_number

    def _format_label(self, datum):
        name = datum['abbrev'] if self.abbreviate_name else datum['name']
        unit = datum['unit']
        error = datum['error']
        prefix = datum['prefix_abbrev'] if self.abbreviate_name else datum['prefix_name']

        if callable(name):
            name = name(self.settings)

        unitname = ''
        if unit is not None:
            q = self.settings.to_preferred_unit(1.0, unit)
            unitname = '{0:~P}'.format(q.units)
            if not unitname: # required for radian and degree
                unitname = '{0:P}'.format(q.units)

        if error:
            fmt = '\u03C3({prefix}{name})'
        else:
            fmt = '{prefix}{name}'

        if unit is not None:
            fmt += ' [{unitname}]'

        return fmt.format(prefix=prefix, name=name, unitname=unitname)

    def _format_value(self, datum):
        value = datum['value']
        unit = datum['unit']
        tolerance = datum['tolerance']

        value = self._convert_value(value, unit)

        if not self.format_number:
            return value

        if isinstance(value, float):
            if tolerance is not None:
                if unit is not None:
                    tolerance = self._convert_value(tolerance, unit)

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

    def _create_datum(self, name, abbrev, value, unit=None, tolerance=None, error=False,
                      prefix_name='', prefix_abbrev=''):
        datum = {'name': name,
                 'abbrev': abbrev,
                 'value': value,
                 'unit': unit,
                 'tolerance': tolerance,
                 'error': error,
                 'prefix_name': prefix_name,
                 'prefix_abbrev': prefix_abbrev}
        return datum

    @abc.abstractmethod
    def build(self):
        raise NotImplementedError


""""""

# Standard library modules.
import abc

# Third party modules.
import pyxray
import numpy as np

# Local modules.
from pymontecarlo.util.tolerance import tolerance_to_decimals
from pymontecarlo.settings import XrayNotation

# Globals and constants variables.


class LazyFormat:
    @abc.abstractmethod
    def format(self, settings):
        raise NotImplementedError


class FormatBuilderBase(metaclass=abc.ABCMeta):
    def __init__(self, settings, abbreviate_name=False, format_number=False):
        self.settings = settings
        self.abbreviate_name = abbreviate_name
        self.format_number = format_number

    def _format_xrayline(self, xrayline):
        if self.settings.preferred_xray_notation == XrayNotation.SIEGBAHN:
            return xrayline.siegbahn
        else:
            return xrayline.iupac

    def _format_label(self, datum):
        name = datum["abbrev"] if self.abbreviate_name else datum["name"]
        unit = datum["unit"]
        error = datum["error"]
        prefix = (
            datum["prefix_abbrev"] if self.abbreviate_name else datum["prefix_name"]
        )

        if isinstance(name, LazyFormat):
            name = name.format(self.settings)
        elif isinstance(name, pyxray.XrayLine):
            name = self._format_xrayline(name)

        unitname = ""
        if unit is not None:
            q = self.settings.to_preferred_unit(1.0, unit)
            unitname = "{0:~P}".format(q.units)
            if not unitname:  # required for radian and degree
                unitname = "{0:P}".format(q.units)

        if error:
            fmt = "\u03C3({prefix}{name})"
        else:
            fmt = "{prefix}{name}"

        if unit is not None:
            fmt += " [{unitname}]"

        return fmt.format(prefix=prefix, name=name, unitname=unitname)

    def _format_value(self, datum):
        value = self._convert_value(datum)

        if not self.format_number:
            return value

        if isinstance(value, (str, int, bool)):
            return str(value)

        if isinstance(value, float):
            if np.isnan(value):
                return "none"

            unit = datum["unit"]
            tolerance = datum["tolerance"]

            if tolerance is not None:
                if unit is not None:
                    tolerance = self._change_unit(tolerance, unit)

                precision = tolerance_to_decimals(tolerance)
                return "{0:.{precision}f}".format(value, precision=precision)
            else:
                return "{:g}".format(value)

        return "{}".format(value)

    def _convert_value(self, datum):
        value = datum["value"]

        if isinstance(value, LazyFormat):
            value = value.format(self.settings)

        if value is None:
            return np.nan

        if isinstance(value, pyxray.XrayLine):
            return self._format_xrayline(value)

        if isinstance(value, float):
            unit = datum["unit"]
            return self._change_unit(value, unit)

        return value

    def _change_unit(self, value, unit):
        if unit is not None:
            q = self.settings.to_preferred_unit(value, unit)
            value = q.magnitude
        return value

    def _create_datum(
        self,
        name,
        abbrev,
        value,
        unit=None,
        tolerance=None,
        error=False,
        prefix_name="",
        prefix_abbrev="",
    ):
        datum = {
            "name": name,
            "abbrev": abbrev,
            "value": value,
            "unit": unit,
            "tolerance": tolerance,
            "error": error,
            "prefix_name": prefix_name,
            "prefix_abbrev": prefix_abbrev,
        }
        return datum

    @abc.abstractmethod
    def build(self):
        raise NotImplementedError

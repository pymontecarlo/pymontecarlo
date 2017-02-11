""""""

# Standard library modules.

# Third party modules.
import pint

# Local modules.

# Globals and constants variables.

ureg = pint.UnitRegistry()

_preferred_units = {}

def set_preferred_unit(unit):
    if isinstance(unit, str):
        unit = ureg.parse_units(unit)

    _, base_unit = ureg._get_base_units(unit)
    _preferred_units[base_unit] = unit

def clear_preferred_units():
    _preferred_units.clear()

def to_preferred_unit(q):
    _, base_unit = ureg._get_base_units(q.units)

    try:
        preferred_unit = _preferred_units[base_unit]
        return q.to(preferred_unit)
    except KeyError:
        return q.to(base_unit)


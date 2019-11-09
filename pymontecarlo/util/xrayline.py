""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.

# Globals and constants variables.


def convert_xrayline(xrayline):
    if isinstance(xrayline, pyxray.XrayLine):
        return xrayline

    try:
        return pyxray.xray_line(*xrayline)
    except:
        raise ValueError('"{}" is not an XrayLine'.format(xrayline))

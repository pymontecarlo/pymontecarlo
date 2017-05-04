""""""

# Standard library modules.
import math

# Third party modules.

# Local modules.

# Globals and constants variables.

def tolerance_to_decimals(tolerance):
    return math.ceil(abs(math.log10(tolerance)))

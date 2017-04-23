"""
Limit based on reaching uncertainty.
"""

# Standard library modules.
import math

# Third party modules.

# Local modules.
from pymontecarlo.options.limit.base import Limit

# Globals and constants variables.

class UncertaintyLimit(Limit):

    UNCERTAINTY_TOLERANCE = 1e-5 # 0.001%

    def __init__(self, xrayline, detector, uncertainty):
        super().__init__()
        self.xrayline = xrayline
        self.detector = detector
        self.uncertainty = uncertainty

    def __repr__(self):
        return '<{classname}({xrayline} <= {uncertainty}%)>' \
            .format(classname=self.__class__.__name__,
                    xrayline=self.xrayline.name,
                    uncertainty=self.uncertainty * 100.0)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.xrayline == other.xrayline and \
            self.detector == other.detector and \
            math.isclose(self.uncertainty, other.uncertainty, abs_tol=self.UNCERTAINTY_TOLERANCE)


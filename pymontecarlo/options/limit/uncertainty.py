"""
Limit based on reaching uncertainty.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.limit.base import Limit

# Globals and constants variables.

class UncertaintyLimit(Limit):

    def __init__(self, xrayline, detector, uncertainty):
        super().__init__()
        self.xrayline = xrayline
        self.detector = detector
        self.uncertainty = uncertainty

    def __repr__(self):
        return '<{classname}({xrayline} <= {uncertainty}%)>' \
            .format(classname=self.__class__.__name__,
                    xrayline=self.xrayline,
                    uncertainty=self.uncertainty * 100.0)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.xrayline == other.xrayline and \
            self.detector == other.detector and \
            self.uncertainty == other.uncertainty

    def create_datarow(self, **kwargs):
        datarow = super().create_datarow(**kwargs)
        datarow.add('uncertainty X-ray line', self.xrayline)
        datarow |= self.detector.create_datarow(**kwargs)
        datarow.add('uncertainty value', self.uncertainty)
        return datarow


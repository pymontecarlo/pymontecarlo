""""""

# Standard library modules.
import collections

# Third party modules.
import pyxray

# Local modules.
import pymontecarlo

# Globals and constants variables.

class XrayLine(collections.namedtuple('XrayLine', ('element', 'line'))):

    def __new__(cls, element, line):
        element = pyxray.element(element)
        try:
            line = pyxray.xray_transition(line)
        except pyxray.NotFound:
            line = pyxray.xray_transitionset(line)
        return super().__new__(cls, element, line)

    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, str(self))

    def __str__(self):
        symbol = pyxray.element_symbol(self.element)

        if self.is_xray_transitionset():
            method = pyxray.xray_transitionset_notation
        else:
            method = pyxray.xray_transition_notation

        settings = pymontecarlo.settings
        preferred_notation = settings.preferred_xrayline_notation
        preferred_encoding = settings.preferred_xrayline_encoding

        notation = method(self.line, preferred_notation, preferred_encoding)

        return '{0} {1}'.format(symbol, notation)

    def is_xray_transitionset(self):
        return isinstance(self.line, pyxray.XrayTransitionSet)

    @property
    def atomic_number(self):
        return self.element.atomic_number


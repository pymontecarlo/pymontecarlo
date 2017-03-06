""""""

# Standard library modules.
import collections

# Third party modules.
import pyxray

# Local modules.

# Globals and constants variables.

_preferred_notation = 'iupac'

def set_preferred_notation(notation):
    global _preferred_notation
    _preferred_notation = notation

_preferred_encoding = 'utf16'

def set_preferred_encoding(encoding):
    global _preferred_encoding
    _preferred_encoding = encoding

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
        notation = method(self.line, _preferred_notation, _preferred_encoding)

        return '{0} {1}'.format(symbol, notation)

    def is_xray_transitionset(self):
        return isinstance(self.line, pyxray.XrayTransitionSet)


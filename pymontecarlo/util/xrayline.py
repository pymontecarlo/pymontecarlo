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

class XrayLine(collections.namedtuple('XrayLine', ('element', 'transition'))):

    def __new__(cls, element, transition):
        element = pyxray.element(element)
        try:
            transition = pyxray.xray_transition(transition)
        except pyxray.NotFound:
            transition = pyxray.xray_transitionset(transition)
        return super().__new__(cls, element, transition)

    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, str(self))

    def __str__(self):
        symbol = pyxray.element_symbol(self.element)

        if isinstance(self.transition, pyxray.XrayTransition):
            method = pyxray.xray_transition_notation
        else:
            method = pyxray.xray_transitionset_notation
        notation = method(self.transition, _preferred_notation, _preferred_encoding)

        return '{0} {1}'.format(symbol, notation)


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
            transition = pyxray.transition(transition)
        except pyxray.NotFound:
            transition = pyxray.transitionset(transition)
        return super().__new__(cls, element, transition)

    def __str__(self):
        symbol = pyxray.element_symbol(self.element)

        if isinstance(self.transition, pyxray.Transition):
            method = pyxray.transition_notation
        else:
            method = pyxray.transitionset_notation
        notation = method(self.transition, _preferred_notation, _preferred_encoding)

        return '{0} {1}'.format(symbol, notation)


""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
import pymontecarlo

# Globals and constants variables.

class XrayLine:

    def __init__(self, element, line):
        self._element = pyxray.element(element)

        try:
            self._line = pyxray.xray_transition(line)
        except pyxray.NotFound:
            self._line = pyxray.xray_transitionset(line)

        self._update_str()

        signal = pymontecarlo.settings.preferred_xrayline_notation_changed
        signal.connect(self._update_str)

        signal = pymontecarlo.settings.preferred_xrayline_encoding_changed
        signal.connect(self._update_str)

    def __hash__(self):
        return hash((self.element, self.line))

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.element == other.element and \
            self.line == other.line

    def __iter__(self):
        return iter((self.element, self.line))

    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, str(self))

    def __str__(self):
        return self._str

    def _update_str(self, *args):
        symbol = pyxray.element_symbol(self.element)

        if self.is_xray_transitionset():
            method = pyxray.xray_transitionset_notation
        else:
            method = pyxray.xray_transition_notation

        settings = pymontecarlo.settings
        preferred_notation = settings.preferred_xrayline_notation
        preferred_encoding = settings.preferred_xrayline_encoding

        try:
            notation = method(self.line, preferred_notation, preferred_encoding)
        except pyxray.NotFound:
            notation = method(self.line, 'iupac', preferred_encoding)

        self._str = '{0} {1}'.format(symbol, notation)

    def is_xray_transitionset(self):
        return isinstance(self.line, pyxray.XrayTransitionSet)

    @property
    def element(self):
        return self._element

    @property
    def atomic_number(self):
        return self.element.atomic_number

    @property
    def line(self):
        return self._line


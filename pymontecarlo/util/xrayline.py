""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.

# Globals and constants variables.

KNOWN_XRAYTRANSITIONS = [pyxray.xray_transition('Ka1'),
                         pyxray.xray_transition('Kb1'),
                         pyxray.xray_transition('La1'),
                         pyxray.xray_transition('Lb1'),
                         pyxray.xray_transition('Ll'),
                         pyxray.xray_transition('Ma1'),
                         pyxray.xray_transition('M4-N2') # Mz
                         ]

def find_lowest_energy_known_xrayline(zs, minimum_energy_eV=0.0):
    lowest_energy_eV = float('inf')
    lowest_xrayline = None

    for z in zs:
        for xraytransition in pyxray.element_xray_transitions(z):
            if xraytransition not in KNOWN_XRAYTRANSITIONS:
                continue

            energy_eV = pyxray.xray_transition_energy_eV(z, xraytransition)
            if energy_eV < lowest_energy_eV and energy_eV >= minimum_energy_eV:
                lowest_xrayline = XrayLine(z, xraytransition)
                lowest_energy_eV = energy_eV

    return lowest_xrayline

class XrayLine:

    def __init__(self, element, line):
        # Ensure pyxray objects
        self._element = pyxray.element(element)

        if not isinstance(line, (pyxray.XrayTransition, pyxray.XrayTransitionSet)):
            try:
                line = pyxray.xray_transition(line)
            except pyxray.NotFound:
                line = pyxray.xray_transitionset(line)
        self._line = line

        self._is_xray_transitionset = isinstance(line, pyxray.XrayTransitionSet)

        # Create names
        symbol = pyxray.element_symbol(self.element)

        if self._is_xray_transitionset:
            method = pyxray.xray_transitionset_notation
        else:
            method = pyxray.xray_transition_notation

        self._iupac = '{} {}'.format(symbol, method(line, 'iupac', 'utf16'))

        try:
            self._siegbahn = '{} {}'.format(symbol, method(line, 'siegbahn', 'utf16'))
        except pyxray.NotFound:
            self._siegbahn = self._iupac

    def __hash__(self):
        return hash((self.element, self.line))

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.element == other.element and \
            self.line == other.line

    def __iter__(self):
        return iter((self.element, self.line))

    def __repr__(self):
        return '<{}({} {})>'.format(self.__class__.__name__,
                                    self._element._repr_inner(),
                                    self._line._repr_inner())

    def is_xray_transitionset(self):
        return self._is_xray_transitionset

    @property
    def element(self):
        return self._element

    @property
    def atomic_number(self):
        return self.element.atomic_number

    @property
    def line(self):
        return self._line

    @property
    def iupac(self):
        return self._iupac

    @property
    def siegbahn(self):
        return self._siegbahn


""""""

# Standard library modules.
import string
from collections import defaultdict
import itertools
import math

# Third party modules.
from pyparsing import Word, Group, Optional, OneOrMore

# Local modules.
import pyxray

# Globals and constants variables.

_symbol = Word(string.ascii_uppercase, string.ascii_lowercase)
_digit = Word(string.digits + ".")
_elementRef = Group(_symbol + Optional(_digit, default="1"))
CHEMICAL_FORMULA_PARSER = OneOrMore(_elementRef)

def from_formula(formula):
    # Parse chemical formula
    formulaData = CHEMICAL_FORMULA_PARSER.parseString(formula)

    zs = []
    atomicfractions = []
    for symbol, atomicfraction in formulaData:
        zs.append(pyxray.element_atomic_number(symbol))
        atomicfractions.append(float(atomicfraction))

    # Calculate total atomic mass
    totalatomicmass = 0.0
    for z, atomicfraction in zip(zs, atomicfractions):
        atomicmass = pyxray.element_atomic_weight(z)
        totalatomicmass += atomicfraction * atomicmass

    # Create composition
    composition = defaultdict(float)

    for z, atomicfraction in zip(zs, atomicfractions):
        atomicmass = pyxray.element_atomic_weight(z)
        weightfraction = atomicfraction * atomicmass / totalatomicmass
        composition[z] += weightfraction

    return composition

def to_atomic(composition):
    """
    Returns a composition :class:`dict` where the values are atomic fractions.

    :arg composition: composition in weight fraction.
        The composition is specified by a dictionary.
        The key are atomic numbers and the values weight fractions.
        No wildcard are accepted.
    :type composition: :class:`dict`
    """
    composition2 = {}

    for z, weightfraction in composition.items():
        composition2[z] = weightfraction / pyxray.element_atomic_weight(z)

    totalfraction = sum(composition2.values())

    for z, fraction in composition2.items():
        try:
            composition2[z] = fraction / totalfraction
        except ZeroDivisionError:
            composition2[z] = 0.0

    return defaultdict(float, composition2)

def process_wildcard(composition):
    """
    Processes element with a wildcard ``?`` weight fraction and returns
    composition balanced to 1.0. 
    """
    composition2 = composition.copy()

    wildcard_zs = set()
    total_wf = 0.0
    for z, wf in composition.items():
        if wf == '?':
            wildcard_zs.add(z)
        else:
            total_wf += wf

    if not wildcard_zs:
        return composition2

    balance_wf = (1.0 - total_wf) / len(wildcard_zs)
    for z in wildcard_zs:
        composition2[z] = balance_wf

    return composition2

def calculate_density_kg_per_m3(composition):
    """
    Returns an estimate density from the composition using the pure element
    density and this equation.

    .. math::

       \\frac{1}{\\rho} = \\sum{\\frac{1}{\\rho_i}}

    :arg composition: composition in weight fraction.
        The composition is specified by a dictionary.
        The key are atomic numbers and the values weight fractions.
        No wildcard are accepted.
    :type composition: :class:`dict`
    """
    density = 0.0

    if not composition:
        return density

    for z, fraction in composition.items():
        density += fraction / pyxray.element_mass_density_kg_per_m3(z)

    return 1.0 / density

def generate_name(composition):
    """
    Generates a name from the composition.
    The name is generated on the basis of a classical chemical formula.

    :arg composition: composition in weight fraction.
        The composition is specified by a dictionary.
        The key are atomic numbers and the values weight fractions.
        No wildcard are accepted.
    :type composition: :class:`dict`
    """
    composition_atomic = to_atomic(composition)

    symbols = []
    fractions = []
    for z in sorted(composition_atomic.keys(), reverse=True):
        symbols.append(pyxray.element_symbol(z))
        fractions.append(int(composition_atomic[z] * 100.0))

    # Find gcd of the fractions
    smallest_gcd = 100
    if len(fractions) >= 2:
        gcds = []
        for a, b in itertools.combinations(fractions, 2):
            gcds.append(math.gcd(a, b))
        smallest_gcd = min(gcds)

    if smallest_gcd == 0.0:
        smallest_gcd = 100.0

    # Write formula
    name = ''
    for symbol, fraction in zip(symbols, fractions):
        fraction /= smallest_gcd
        if fraction == 0:
            continue
        elif fraction == 1:
            name += "%s" % symbol
        else:
            name += '%s%i' % (symbol, fraction)

    if not name:
        name = 'Untitled'

    return name

#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- Material definition
================================================================================

.. module:: material
   :synopsis: Material definition

.. inheritance-diagram:: pymontecarlo.input.material

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['Material',
           'VACUUM']

# Standard library modules.
from fractions import gcd
from itertools import combinations
from collections import defaultdict
import string
import numbers

# Third party modules.
from pyparsing import Word, Group, Optional, OneOrMore
import pyxray.element_properties as ep

# Local modules.

# Globals and constants variables.

_symbol = Word(string.ascii_uppercase, string.ascii_lowercase)
_digit = Word(string.digits + ".")
_elementRef = Group(_symbol + Optional(_digit, default="1"))
CHEMICAL_FORMULA_PARSER = OneOrMore(_elementRef)

class _constant_factory(object):

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return str(self._value)

    def __call__(self, *args, **kwargs):
        return self._value

class Material(object):

    DEFAULT_ABSORPTION_ENERGY_eV = 50.0

    def __init__(self, composition, name=None, density_kg_m3=None,
                 absorption_energy_eV=None, *args, **kwargs):
        """
        Creates a new material.

        :arg name: name of the material
        :type name: :class:`str`

        :arg composition: composition in weight fraction.
            The composition is specified by a dictionary.
            The key can either be the atomic number or the symbol of the element.
            It will automatically be converted to the atomic number.
            The value is the weight fraction between ]0.0, 1.0] or ``?``
            indicating that the weight fraction is unknown and shall be
            automatically calculated to make the total weight fraction equal
            to 1.0.
        :type composition: :class:`dict`

        :arg density_kg_m3: material's density in kg/m3.
            If the density is ``None`` or less than 0 (default), it will be
            automatically calculated based on the density of the elements and
            their weight fraction.
        :type density_kg_m3: :class:`float`
        """
        composition = self.calculate_composition(composition)
        self._composition = composition
        self._composition_atomic = self.calculate_composition_atomic(composition)

        if name is None:
            name = self.generate_name(composition)
        self._name = name

        if density_kg_m3 is None:
            density_kg_m3 = self.calculate_density(composition)
        self._density_kg_m3 = density_kg_m3

        if isinstance(absorption_energy_eV, numbers.Number):
            self._absorption_energy_eV = \
                defaultdict(_constant_factory(absorption_energy_eV))
        else:
            self._absorption_energy_eV = \
                defaultdict(_constant_factory(self.DEFAULT_ABSORPTION_ENERGY_eV))
        if absorption_energy_eV is not None:
            self._absorption_energy_eV.update(absorption_energy_eV)

    @staticmethod
    def calculate_composition(composition):
        # Replace symbol keys with integer
        for key in list(composition.keys()):
            if isinstance(key, str):
                composition[ep.atomic_number(key)] = composition.pop(key)

        # Replace wildcard
        totalfraction = 0.0
        countwildcard = 0
        for z, fraction in composition.items():
            if z <= 0 or z >= 99:
                raise ValueError("Atomic number '%i' must be between [1, 99]" % z)
            if fraction == '?':
                countwildcard += 1
            else:
                totalfraction += float(fraction)

        if countwildcard > 0:
            if totalfraction <= 1.0:
                wildcardfraction = (1.0 - totalfraction) / float(countwildcard)
            else:
                raise ValueError('Wild card(s) could not be replaced since total fraction is already 1.0')

        for z, fraction in composition.items():
            if fraction == '?':
                fraction = wildcardfraction
            composition[z] = float(fraction)

        # Check total fraction
        totalfraction = sum(composition.values())
        if abs(totalfraction - 1.0) > 1e-6:
            raise ValueError("The total weight fraction (%s) should be 1.0." % totalfraction)

        return defaultdict(float, composition)

    @staticmethod
    def calculate_composition_atomic(composition):
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
            composition2[z] = weightfraction / ep.atomic_mass_kg_mol(z)

        totalfraction = sum(composition2.values())

        for z, fraction in composition2.items():
            composition2[z] = fraction / totalfraction

        return defaultdict(float, composition2)

    @staticmethod
    def composition_from_formula(formula):
        # Parse chemical formula
        formulaData = CHEMICAL_FORMULA_PARSER.parseString(formula)

        zs = []
        atomicfractions = []
        for symbol, atomicfraction in formulaData:
            zs.append(ep.atomic_number(symbol=symbol))
            atomicfractions.append(float(atomicfraction))

        # Calculate total atomic mass
        totalatomicmass = 0.0
        for z, atomicfraction in zip(zs, atomicfractions):
            atomicmass = ep.atomic_mass_kg_mol(z)
            totalatomicmass += atomicfraction * atomicmass

        # Create composition
        composition = defaultdict(float)

        for z, atomicfraction in zip(zs, atomicfractions):
            atomicmass = ep.atomic_mass_kg_mol(z)
            weightfraction = atomicfraction * atomicmass / totalatomicmass
            composition[z] += weightfraction

        return composition

    @staticmethod
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
        composition_atomic = Material.calculate_composition_atomic(composition)

        symbols = []
        fractions = []
        for z in sorted(composition_atomic.keys(), reverse=True):
            symbols.append(ep.symbol(z))
            fractions.append(int(composition_atomic[z] * 100.0))

        # Find gcd of the fractions
        smallest_gcd = 100
        if len(fractions) >= 2:
            gcds = []
            for a, b in combinations(fractions, 2):
                gcds.append(gcd(a, b))
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

        return name

    @staticmethod
    def calculate_density(composition):
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

        for z, fraction in composition.items():
            density += fraction / ep.mass_density_kg_m3(z)

        return 1.0 / density

    @classmethod
    def pure(cls, z, absorption_energy_eV=None):
        """
        Returns the material for the specified pure element.

        :arg z: atomic number
        :type z: :class:`int`

        :arg absorption_energy_eV: absorption energy of the different particles
        :type absorption_energy_eV: :class:`dict`
        """
        name = ep.name(z)
        composition = {z: 1.0}
        density_kg_m3 = ep.mass_density_kg_m3(z)

        return cls(composition, name, density_kg_m3, absorption_energy_eV)

#     @classmethod
#     def from_composition_atomic(cls, composition, name=None,
#                                 density_kg_m3=None, absorption_energy_eV=None):
#         pass

    @classmethod
    def from_formula(cls, formula, density_kg_m3=None,
                     absorption_energy_eV=None):
        composition = cls.composition_from_formula(formula)
        return cls(composition, formula, density_kg_m3, absorption_energy_eV)

    def __repr__(self):
        return '<Material(name=%s, composition=%s, density=%s kg/m3, absorption energies=%s)>' % \
            (self.name, self.composition, self.density_kg_m3, self.absorption_energy_eV)

    def __str__(self):
        return self.name

    @property
    def name(self):
        """
        Name of material. Immutable cannot be modified.
        """
        return self._name

    @property
    def composition(self):
        """
        Composition of material in weight fraction. Immutable cannot be modified.
        """
        return self._composition.copy()

    composition_weight = composition

    @property
    def composition_atomic(self):
        """
        Composition of material in atomic fraction. Immutable cannot be modified.
        """
        return self._composition_atomic.copy()

    @property
    def density_kg_m3(self):
        """
        Density of material in kg/m3. Immutable cannot be modified.
        """
        return self._density_kg_m3

    @property
    def density_g_cm3(self):
        """
        Density of material in g/cm3. Immutable cannot be modified.
        """
        return self._density_kg_m3 / 1000.0

    @property
    def absorption_energy_eV(self):
        """
        Absorption energy(ies) of particles inside the material.
        Immutable cannot be modified.
        """
        return self._absorption_energy_eV.copy()

class _Vacuum(Material):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            inst = Material.__new__(cls, *args, **kwargs)
            inst._name = 'Vacuum'
            inst._composition = {}
            inst._composition_atomic = {}
            inst._density_kg_m3 = 0.0
            inst._absorption_energy_eV = defaultdict(lambda: 0.0)
            cls._instance = inst
        return cls._instance

    def __init__(self):
        pass

    def __repr__(self):
        return '<Vacuum()>'

    def __copy__(self):
        return VACUUM

    def __deepcopy__(self, memo):
        return VACUUM

    def __getstate__(self):
        return {} # Nothing to pickle

    def __reduce__(self):
        return (self.__class__, ())

VACUUM = _Vacuum()

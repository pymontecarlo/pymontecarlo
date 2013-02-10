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

# Standard library modules.
from collections import defaultdict
from fractions import gcd
from itertools import combinations

# Third party modules.
from pyparsing import Word, Group, Optional, OneOrMore

# Local modules.
from pymontecarlo.input.option import Option

import pymontecarlo.util.element_properties as ep
from pymontecarlo.util.xmlutil import XMLIO, Element

# Globals and constants variables.

def _calculate_composition(composition):
    """
    Returns a valid composition :class:`dict`.
    Replaces wildcards and ensures that the total fraction is equal to 1.0.
    
    :arg composition: composition in weight fraction. 
        The composition is specified by a dictionary.
        The key can either be the atomic number or the symbol of the element.
        It will automatically be converted to the atomic number.
        The value is the weight fraction between ]0.0, 1.0] or ``?`` 
        indicating that the weight fraction is unknown and shall be 
        automatically calculated to make the total weight fraction equal 
        to 1.0. 
    :type composition: :class:`dict`
    """
    if not composition:
        raise ValueError, 'No elements defined'

    composition2 = {}
    for element, fraction in composition.iteritems():
        # Replace symbol by atomic number
        if isinstance(element, basestring): # symbol
            element = ep.atomic_number(symbol=element)

        # Atomic number check
        if element <= 0 or element > 96:
            raise ValueError, "Atomic number (%i) must be between [1, 96]" % element

        # Fraction check
        if fraction != '?':
            fraction = float(fraction)
            if fraction <= 0.0 or fraction > 1.0:
                raise ValueError, "Fraction (%s) must be between ]0.0, 1.0]" % fraction

        composition2[element] = fraction

    # Replace wildcard
    totalfraction = 0.0
    countwildcard = 0
    for fraction in composition2.values():
        if fraction == '?':
            countwildcard += 1
        else:
            totalfraction += fraction

    if countwildcard > 0:
        if totalfraction < 1.0:
            wildcardfraction = (1.0 - totalfraction) / float(countwildcard)
        else:
            raise ValueError, 'Wild card(s) could not be replaced since total fraction is already 1.0'

    composition3 = {}
    for z, fraction in composition2.iteritems():
        if fraction == '?':
            fraction = wildcardfraction
        composition3[z] = fraction

    # Check total fraction
    totalfraction = sum(composition3.values())
    if abs(totalfraction - 1.0) > 1e-6:
        raise ValueError, "The total weight fraction (%s) should be 1.0." % totalfraction

    return composition3

def _calculate_composition_atomic(composition):
    """
    Returns a composition :class:`dict` where the values are atomic fractions.
    
    :arg composition: composition in weight fraction. 
        The composition is specified by a dictionary.
        The key are atomic numbers and the values weight fractions.
        No wildcard are accepted.
    :type composition: :class:`dict`
    """
    composition2 = {}

    for z, weightfraction in composition.iteritems():
        composition2[z] = weightfraction / ep.atomic_mass(z)

    totalfraction = sum(composition2.values())

    for z, fraction in composition2.iteritems():
        composition2[z] = fraction / totalfraction

    return composition2

def _calculate_density(composition):
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

    for z, fraction in composition.iteritems():
        density += fraction / ep.mass_density(z)

    return 1.0 / density

def _generate_name(composition):
    """
    Generates a name from the composition. 
    The name is generated on the basis of a classical chemical formula.
    
    :arg composition: composition in weight fraction. 
        The composition is specified by a dictionary.
        The key are atomic numbers and the values weight fractions.
        No wildcard are accepted.
    :type composition: :class:`dict`
    """
    composition_atomic = _calculate_composition_atomic(composition)

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

    # Write formula
    name = ''
    for symbol, fraction in zip(symbols, fractions):
        fraction /= smallest_gcd
        if fraction == 1:
            name += "%s" % symbol
        else:
            name += '%s%i' % (symbol, fraction)

    return name

def composition_from_formula(formula):
    """
    Returns a dictionary when the keys are the atomic numbers and the values 
    the weight fraction from the specified chemical formula.
    
    :arg formula: chemical formula (e.g. ``'AlB2Zr5'``).
    """
    # Parse chemical formula
    caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowers = caps.lower()
    digits = "0124356789."

    element = Word(caps, lowers)
    integer = Word(digits)
    elementRef = Group(element + Optional(integer, default="1"))
    chemicalFormula = OneOrMore(elementRef)

    formulaData = chemicalFormula.parseString(formula)

    zs = []
    atomicfractions = []
    for symbol, atomicfraction in formulaData:
        zs.append(ep.atomic_number(symbol=symbol))
        atomicfractions.append(float(atomicfraction))

    # Calculate total atomic mass
    totalatomicmass = 0.0
    for z, atomicfraction in zip(zs, atomicfractions):
        atomicmass = ep.atomic_mass(z)
        totalatomicmass += atomicfraction * atomicmass

    # Create composition
    composition = defaultdict(float)

    for z, atomicfraction in zip(zs, atomicfractions):
        atomicmass = ep.atomic_mass(z)
        weightfraction = atomicfraction * atomicmass / totalatomicmass

        composition[z] += weightfraction

    return composition

def pure(z,
         absorption_energy_electron_eV=50.0,
         absorption_energy_photon_eV=50.0,
         absorption_energy_positron_eV=50.0):
    """
    Returns the material for the specified pure element.
    
    :arg z: atomic number
    :type z: :class:`int`
    
    :arg absorption_energy_electron_eV: absorption energy of the electrons in
            this material.
    :type absorption_energy_electron_eV: :class:`float`
    
    :arg absorption_energy_photon_eV: absorption energy of the photons in
        this material.
    :type absorption_energy_photon_eV: :class:`float`
    
    :arg absorption_energy_positron_eV: absorption energy of the positrons in
        this material.
    :type absorption_energy_positron_eV: :class:`float`
    """
    name = ep.name(z)
    composition = {z: '?'}

    return Material(name, composition, None,
                    absorption_energy_electron_eV, absorption_energy_photon_eV,
                    absorption_energy_positron_eV)

class Material(Option):
    def __init__(self, name, composition, density_kg_m3=None,
                 absorption_energy_electron_eV=50.0,
                 absorption_energy_photon_eV=50.0,
                 absorption_energy_positron_eV=50.0):
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
        
        :arg absorption_energy_electron_eV: absorption energy of the electrons 
            in this material.
        :type absorption_energy_electron_eV: :class:`float`
        
        :arg absorption_energy_photon_eV: absorption energy of the photons in
            this material.
        :type absorption_energy_photon_eV: :class:`float`
        
        :arg absorption_energy_positron_eV: absorption energy of the positrons
            in this material.
        :type absorption_energy_positron_eV: :class:`float`
        """
        Option.__init__(self)

        self.name = name
        self.composition = composition
        self.density_kg_m3 = density_kg_m3

        self.absorption_energy_electron_eV = absorption_energy_electron_eV
        self.absorption_energy_photon_eV = absorption_energy_photon_eV
        self.absorption_energy_positron_eV = absorption_energy_positron_eV

    def __repr__(self):
        return '<Material(name=%s, composition=%s, density=%s kg/m3, abs_electron=%s eV, abs_photon=%s eV, abs_positron=%s eV)>' % \
            (self.name, self.composition, self.density_kg_m3,
             self.absorption_energy_electron_eV,
             self.absorption_energy_photon_eV,
             self.absorption_energy_positron_eV)

    def __str__(self):
        return self.name

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        name = element.get('name')

        composition = {}
        for child in iter(element.find('composition')):
            composition[int(child.get('z'))] = float(child.get('weightFraction'))

        density_kg_m3 = float(element.get('density'))

        abs_electron_eV = float(element.get('absorptionEnergyElectron'))
        abs_photon_eV = float(element.get('absorptionEnergyPhoton'))
        abs_positron_eV = float(element.get('absorptionEnergyPositron'))

        return cls(name, composition, density_kg_m3,
                   abs_electron_eV, abs_photon_eV, abs_positron_eV)

    def __savexml__(self, element, *args, **kwargs):
        element.set('name', self.name)

        child = Element('composition')
        for z, fraction in self.composition.iteritems():
            child.append(Element('element', {'z': str(z), 'weightFraction': str(fraction)}))
        element.append(child)

        element.set('density', str(self.density_kg_m3))

        element.set('absorptionEnergyElectron', str(self.absorption_energy_electron_eV))
        element.set('absorptionEnergyPhoton', str(self.absorption_energy_photon_eV))
        element.set('absorptionEnergyPositron', str(self.absorption_energy_positron_eV))

    @property
    def name(self):
        """
        Name of the material.
        """
        return self._props['name']

    @name.setter
    def name(self, name):
        self._props['name'] = name

    @property
    def composition(self):
        """
        Composition of this material.
        The composition is specified by a dictionary.
        The keys are atomic numbers and values are weight fractions.
        """
        return dict(self._props['composition']) # copy

    @composition.setter
    def composition(self, composition):
        composition = _calculate_composition(composition)
        self._props['composition'] = composition
        self._props['composition_atomic'] = \
            _calculate_composition_atomic(composition)

    @property
    def composition_atomic(self):
        """
        Returns the composition of this material.
        The composition is specified by a dictionary.
        The keys are atomic numbers and values are atomic fractions.
        """
        return self._props['composition_atomic']

    @property
    def density_kg_m3(self):
        """
        Density of this material in kg/m3.
        """
        if self.has_density_defined():
            return self._props['density']
        else:
            return _calculate_density(self.composition)

    @density_kg_m3.setter
    def density_kg_m3(self, density):
        self._props['density'] = density

    @density_kg_m3.deleter
    def density_kg_m3(self):
        self._props['density'] = None

    def has_density_defined(self):
        """
        Returns ``True`` if the density was specified by the user, ``False`` if
        it is automatically calculated from the composition.
        """
        density = self._props['density']
        return density is not None and density >= 0.0

    @property
    def absorption_energy_electron_eV(self):
        """
        Absorption energy of the electrons in this material.
        """
        return self._props['absorption energy electron']

    @absorption_energy_electron_eV.setter
    def absorption_energy_electron_eV(self, energy):
        if energy < 0.0:
            raise ValueError, "Absorption energy (%s) must be greater or equal to 0.0" \
                    % energy
        self._props['absorption energy electron'] = energy

    @property
    def absorption_energy_photon_eV(self):
        """
        Absorption energy of the photons in this material.
        """
        return self._props['absorption energy photon']

    @absorption_energy_photon_eV.setter
    def absorption_energy_photon_eV(self, energy):
        if energy < 0.0:
            raise ValueError, "Absorption energy (%s) must be greater or equal to 0.0" \
                    % energy
        self._props['absorption energy photon'] = energy

    @property
    def absorption_energy_positron_eV(self):
        """
        Absorption energy of the positrons in this material.
        """
        return self._props['absorption energy positron']

    @absorption_energy_positron_eV.setter
    def absorption_energy_positron_eV(self, energy):
        if energy < 0.0:
            raise ValueError, "Absorption energy (%s) must be greater or equal to 0.0" \
                    % energy
        self._props['absorption energy positron'] = energy

XMLIO.register('{http://pymontecarlo.sf.net}material', Material)

class _Vacuum(Option):
    def __init__(self):
        Option.__init__(self)
        self._index = 0

    def __repr__(self):
        return '<Vacuum()>'

    def __str__(self):
        return self.name

    def __copy__(self):
        return VACUUM

    def __deepcopy__(self, memo):
        return VACUUM

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        return VACUUM

    @property
    def name(self):
        return 'Vacuum'

    @property
    def composition(self):
        return {}

    @property
    def composition_atomic(self):
        return {}

    @property
    def density_kg_m3(self):
        return 0.0

    def has_density_defined(self):
        return False

VACUUM = _Vacuum()

XMLIO.register('{http://pymontecarlo.sf.net}vacuum', _Vacuum)

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

__all__ = ['composition_from_formula',
           'pure',
           'Material',
           'VACUUM']

# Standard library modules.
from collections import defaultdict
from fractions import gcd
from itertools import combinations
from types import StringTypes
import warnings

# Third party modules.
from pyparsing import Word, Group, Optional, OneOrMore

# Local modules.
from pymontecarlo.input.particle import PARTICLES, ParticleType
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, FrozenParameter, SimpleValidator,
     ParameterizedMutableMapping, FactorParameterAlias, expand, freeze)
from pymontecarlo.input.xmlmapper import \
    (mapper, ParameterizedAttribute, ParameterizedElementDict,
     _XMLType, PythonType)

import pyxray.element_properties as ep

# Globals and constants variables.

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
        composition2[z] = weightfraction / ep.atomic_mass_kg_mol(z)

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
        density += fraction / ep.mass_density_kg_m3(z)

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
        atomicmass = ep.atomic_mass_kg_mol(z)
        totalatomicmass += atomicfraction * atomicmass

    # Create composition
    composition = defaultdict(float)

    for z, atomicfraction in zip(zs, atomicfractions):
        atomicmass = ep.atomic_mass_kg_mol(z)
        weightfraction = atomicfraction * atomicmass / totalatomicmass

        composition[z] += weightfraction

    return composition

def pure(z):
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

    mat = Material(name, composition, None)
    mat.calculate()

    return mat

class _Composition(ParameterizedMutableMapping):
    
    def __init__(self):
        validator = SimpleValidator(lambda wf: 0.0 <= wf <= 1.0 or wf == '?',
                                    'Weight fraction must be within [0.0, 1.0]')
        ParameterizedMutableMapping.__init__(self, validators=[validator])

    def __setitem__(self, key, value):
        if isinstance(key, StringTypes):
            key = ep.atomic_number(key)
        if key <= 0 or key >= 99:
            raise ValueError, "Atomic number must be between [1, 99]"
        ParameterizedMutableMapping.__setitem__(self, key, value)
    
    def calculate(self):
        compositions = expand(self)
        
        # Replace wildcard
        for composition in compositions:
            # Replace wildcard
            totalfraction = 0.0
            countwildcard = 0
            for fraction in composition.values():
                if fraction == '?':
                    countwildcard += 1
                else:
                    totalfraction += fraction

            if countwildcard > 0:
                if totalfraction <= 1.0:
                    wildcardfraction = (1.0 - totalfraction) / float(countwildcard)
                else:
                    raise ValueError, 'Wild card(s) could not be replaced since total fraction is already 1.0'

            for z, fraction in composition.items():
                if fraction == '?':
                    fraction = wildcardfraction
                composition[z] = fraction

            # Check total fraction
            totalfraction = sum(composition.values())
            if abs(totalfraction - 1.0) > 1e-6:
                raise ValueError, "The total weight fraction (%s) should be 1.0." % totalfraction

        # Replace values
        self.clear()

        zs = {}
        for composition in compositions:
            for z, wf in composition.iteritems():
                zs.setdefault(z, []).append(wf)

        for z, wfs in zs.iteritems():
            self[z] = wfs

class _WeightFractionXMLType(_XMLType):
    
    def to_xml(self, value):
        return str(value)

    def from_xml(self, value):
        if value != '?':
            value = float(value)
        return value

class _DensityParameter(Parameter):
    
    def __init__(self, doc="Density"):
        validator = SimpleValidator(lambda d: d is None or d >= 0.0,
                                    "Density must be greater than 0.0")
        Parameter.__init__(self, [validator], doc)

    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)
        methods[name + '_kg_m3'] = parameter
        methods[name + '_g_cm3'] = FactorParameterAlias(parameter, 1000.0)
        Parameter._new(self, cls, clsname, bases, methods, name + "_kg_m3")

class _AbsorptionEnergy(ParameterizedMutableMapping):

    def __init__(self, default_energy_eV=50.0):
        validator = SimpleValidator(lambda e: e >= 0.0,
                                    'Energy must be greater or equal to 0.0')
        ParameterizedMutableMapping.__init__(self, validators=[validator])

        self._default_energy_eV = default_energy_eV

    def __setitem__(self, key, value):
        if key not in PARTICLES:
            raise KeyError, "Unknown particle: %s" % key
        ParameterizedMutableMapping.__setitem__(self, key, value)

    def __getitem__(self, key):
        if key not in self.__parameters__:
            return self._default_energy_eV
        return self.__parameters__[key].__get__(self)

class Material(object):

    __metaclass__ = ParameterizedMetaClass

    name = Parameter(doc="Name")

    composition = FrozenParameter(_Composition, "Composition")

    density = _DensityParameter()

    absorption_energy_eV = \
        FrozenParameter(_AbsorptionEnergy,
                        "Absorption energy of particles (in eV)")

    def __init__(self, name, composition, density_kg_m3=None):
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
        self.name = name

        self.composition.update(composition)

        self.density_kg_m3 = density_kg_m3

        self.absorption_energy_eV.clear()

    def __repr__(self):
        return '<Material(name=%s, composition=%s, density=%s kg/m3, abs_electron=%s eV, abs_photon=%s eV, abs_positron=%s eV)>' % \
            (self.name, self.composition, self.density_kg_m3,
             self.absorption_energy_electron_eV,
             self.absorption_energy_photon_eV,
             self.absorption_energy_positron_eV)

    def __str__(self):
        return self.name

    def calculate(self):
        self.composition.calculate()

        # Calculate density
        if self.density_kg_m3 is None:
            if len(expand(self.composition)) != 1:
                message = "Cannot calculate density when many compositions are defined"
                warnings.warn(message, UserWarning)
            else:
                self.density_kg_m3 = _calculate_density(self.composition)

    def has_density_defined(self):
        """
        Returns ``True`` if the density was specified by the user, ``False`` if
        it is automatically calculated from the composition.
        """
        density = self.density_kg_m3
        return density is not None and density >= 0.0

mapper.register(Material, '{http://pymontecarlo.sf.net}material',
                ParameterizedAttribute('name', PythonType(str)),
                ParameterizedElementDict('composition', PythonType(int), _WeightFractionXMLType(),
                                        keyxmlname='z', valuexmlname='element'),
                ParameterizedAttribute('density_kg_m3', PythonType(float), 'density'),
                ParameterizedElementDict('absorption_energy_eV', ParticleType(), PythonType(float),
                                         "absorption_energy", "particle", "energy"),)

class _Vacuum(Material):
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            inst = Material.__new__(cls, *args, **kwargs)
            inst.name = 'Vacuum'
            inst.composition.clear()
            inst.density_kg_m3 = 0.0
            inst.absorption_energy_eV._default_energy_eV = 0.0
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

    def calculate(self):
        pass

    def has_density_defined(self):
        return False

VACUUM = _Vacuum()
freeze(VACUUM)

mapper.register(_Vacuum, '{http://pymontecarlo.sf.net}vacuum', inherit=False)

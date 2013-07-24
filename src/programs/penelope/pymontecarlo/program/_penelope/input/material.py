#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- PENELOPE material definition
================================================================================

.. module:: material
   :synopsis: PENELOPE material definition

.. inheritance-diagram:: pymontecarlo.program._penelope.input.material

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from collections import namedtuple

# Third party modules.
import pyxray.element_properties as ep

# Local modules.
from pymontecarlo.input.material import Material as _Material
from pymontecarlo.input.parameter import \
    Parameter, UnitParameter, SimpleValidator, CastValidator
from pymontecarlo.input.xmlmapper import \
    (mapper, Attribute, ParameterizedAttribute, ParameterizedElement, UserType,
     PythonType)

# Globals and constants variables.

def pure(z,
         absorption_energy_electron_eV=50.0, absorption_energy_photon_eV=50.0,
         absorption_energy_positron_eV=50.0,
         elastic_scattering=(0.0, 0.0),
         cutoff_energy_inelastic_eV=50.0, cutoff_energy_bremsstrahlung_eV=50.0):
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
    
    :arg elastic_scattering: elastic scattering coefficients. 
        They can either be specified as a :class:`tuple`: ``(C1, C2)`` or
        as a single :class:`float` value, where ``C1=C2``. 
        The value of C1 or C2 must be between 0.0 and 0.2 inclusively.
    :type elastic_scattering: :class:`tuple` or :class:`float`
    
    :arg cutoff_energy_inelastic_eV: cutoff energy for inelastic collisions
        (in eV).
    
    :arg cutoff_energy_bremsstrahlung_eV: cutoff energy for Bremsstrahlung
        emission (in eV).
    """
    name = ep.name(z)
    composition = {z: '?'}

    mat = Material(name, composition, None,
                   absorption_energy_electron_eV, absorption_energy_photon_eV,
                   absorption_energy_positron_eV,
                   elastic_scattering,
                   cutoff_energy_inelastic_eV, cutoff_energy_bremsstrahlung_eV)
    mat.calculate()

    return mat

elastic_scattering = namedtuple('elastic_scattering', ['c1', 'c2'])

mapper.register(elastic_scattering,
                '{http://pymontecarlo.sf.net/penelope}elastic_scattering',
                Attribute('c1', PythonType(float)),
                Attribute('c2', PythonType(float)))

_elastic_scattering_validator = \
    SimpleValidator(lambda es: 0.0 <= es.c1 <= 0.2 and 0.0 <= es.c2 <= 0.2)
_cutoff_energy_validator = SimpleValidator(lambda e: e >= 0.0)

class Material(_Material):

    elastic_scattering = \
        Parameter([CastValidator(elastic_scattering),
                   _elastic_scattering_validator],
                  "Elastic scattering coefficients (C1 and C2)")

    cutoff_energy_inelastic = \
        UnitParameter('eV', _cutoff_energy_validator,
                      "Cutoff energy for inelastic collisions")

    cutoff_energy_bremsstrahlung = \
        UnitParameter('eV', _cutoff_energy_validator,
                      "Cutoff energy for Bremsstrahlung emission")

    def __init__(self, name, composition, density_kg_m3=None,
                 absorption_energy_electron_eV=50.0,
                 absorption_energy_photon_eV=50.0,
                 absorption_energy_positron_eV=50.0,
                 elastic_scattering=(0.0, 0.0),
                 cutoff_energy_inelastic_eV=50.0, cutoff_energy_bremsstrahlung_eV=50.0):
        """
        Creates a new material.
        
        :arg name: name of the material
        :type name: :class:`str`
        
        :arg composition: composition in weight fraction. 
            The composition is specified by a list of tuples.
            The first element of each tuple can either be the atomic number or
            the symbol of the element.
            It will automatically be converted to the atomic number.
            The second is the weight fraction between ]0.0, 1.0] or ``?`` 
            indicating that the weight fraction is unknown and shall be 
            automatically calculated to make the total weight fraction equal 
            to 1.0. 
        :type composition: :class:`list`
        
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
        
        :arg absorption_energy_positron_eV: absorption energy of the positrons in
            this material.
        :type absorption_energy_positron_eV: :class:`float`
        
        :arg elastic_scattering: elastic scattering coefficients. 
            They can either be specified as a :class:`tuple`: ``(C1, C2)`` or
            as a single :class:`float` value, where ``C1=C2``. 
            The value of C1 or C2 must be between 0.0 and 0.2 inclusively.
        :type elastic_scattering: :class:`tuple` or :class:`float`
        
        :arg cutoff_energy_inelastic_eV: cutoff energy for inelastic collisions
            (in eV).
        
        :arg cutoff_energy_bremsstrahlung_eV: cutoff energy for Bremsstrahlung
            emission (in eV).
        """
        _Material.__init__(self, name, composition, density_kg_m3,
                           absorption_energy_electron_eV,
                           absorption_energy_photon_eV,
                           absorption_energy_positron_eV)

        self.elastic_scattering = elastic_scattering
        self.cutoff_energy_inelastic_eV = cutoff_energy_inelastic_eV
        self.cutoff_energy_bremsstrahlung_eV = cutoff_energy_bremsstrahlung_eV

    def __repr__(self):
        return '<PenelopeMaterial(name=%s, composition=%s, density=%s kg/m3, abs_electron=%s eV, abs_photon=%s eV, abs_positron=%s eV, elastic_scattering=%s, cutoff_inelastic=%s eV, cutoff_bremsstrahlung=%s eV)>' % \
            (self.name, self.composition, self.density_kg_m3,
             self.absorption_energy_electron_eV, self.absorption_energy_photon_eV,
             self.absorption_energy_positron_eV,
             self.elastic_scattering,
             self.cutoff_energy_inelastic_eV, self.cutoff_energy_bremsstrahlung_eV)

mapper.register(Material, '{http://pymontecarlo.sf.net/penelope}material',
                ParameterizedElement('elastic_scattering', UserType(elastic_scattering)),
                ParameterizedAttribute('cutoff_energy_inelastic_eV', PythonType(float), 'wcc'),
                ParameterizedAttribute('cutoff_energy_bremsstrahlung_eV', PythonType(float), 'wcr'))

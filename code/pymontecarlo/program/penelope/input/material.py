#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- PENELOPE material definition
================================================================================

.. module:: material
   :synopsis: PENELOPE material definition

.. inheritance-diagram:: material

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.input.material import Material as _Material
from pymontecarlo.input.option import Option
import pymontecarlo.util.element_properties as ep
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

def pure(z, absorption_energy_electron_eV=50.0, absorption_energy_photon_eV=50.0,
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

    return Material(name, composition, None,
                    absorption_energy_electron_eV, absorption_energy_photon_eV,
                    elastic_scattering,
                    cutoff_energy_inelastic_eV, cutoff_energy_bremsstrahlung_eV)

class Material(_Material, Option):
    def __init__(self, name, composition, density_kg_m3=None,
                 absorption_energy_electron_eV=50.0, absorption_energy_photon_eV=50.0,
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
        Option.__init__(self)
        _Material.__init__(self, name, composition, density_kg_m3,
                           absorption_energy_electron_eV, absorption_energy_photon_eV)

        self.elastic_scattering = elastic_scattering
        self.cutoff_energy_inelastic_eV = cutoff_energy_inelastic_eV
        self.cutoff_energy_bremsstrahlung_eV = cutoff_energy_bremsstrahlung_eV

    def __repr__(self):
        return '<PenelopeMaterial(name=%s, composition=%s, density=%s kg/m3, abs_electron=%s eV, abs_photon=%s eV, elastic_scattering=%s, cutoff_inelastic=%s eV, cutoff_bremsstrahlung=%s eV)>' % \
            (self.name, self.composition, self.density_kg_m3,
             self.absorption_energy_electron_eV, self.absorption_energy_photon_eV,
             self.elastic_scattering,
             self.cutoff_energy_inelastic_eV, self.cutoff_energy_bremsstrahlung_eV)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        material = _Material.__loadxml__(element, *args, **kwargs)

        elastic_scattering = (float(element.get('c1')), float(element.get('c2')))
        cutoff_energy_inelastic = float(element.get('wcc'))
        cutoff_energy_bremsstrahlung = float(element.get('wcr'))

        return cls(material.name, material.composition, material.density_kg_m3,
                   material.absorption_energy_electron_eV, material.absorption_energy_photon_eV,
                   elastic_scattering,
                   cutoff_energy_inelastic, cutoff_energy_bremsstrahlung)

    def __savexml__(self, element, *args, **kwargs):
        _Material.__savexml__(self, element, *args, **kwargs)

        element.set('c1', str(self.elastic_scattering[0]))
        element.set('c2', str(self.elastic_scattering[1]))
        element.set('wcc', str(self.cutoff_energy_inelastic_eV))
        element.set('wcr', str(self.cutoff_energy_bremsstrahlung_eV))

    @property
    def elastic_scattering(self):
        """
        Elastic scattering coefficients.
        :rtype: :class:`tuple` 
        """
        return self._props['elastic scattering']

    @elastic_scattering.setter
    def elastic_scattering(self, coeffs):
        try:
            c1, c2 = coeffs
        except TypeError:
            c1 = c2 = float(coeffs)

        if c1 < 0.0 or c1 > 0.2:
            raise ValueError, "C1 elastic scattering coefficient (%s) must be between [0.0, 0.2]" % c1
        if c2 < 0.0 or c2 > 0.2:
            raise ValueError, "C2 elastic scattering coefficient (%s) must be between [0.0, 0.2]" % c2

        self._props['elastic scattering'] = (c1, c2)

    @property
    def cutoff_energy_inelastic_eV(self):
        """
        Cutoff energy for inelastic collisions (in eV).
        """
        return self._props['cutoff energy inelastic']

    @cutoff_energy_inelastic_eV.setter
    def cutoff_energy_inelastic_eV(self, energy):
        if energy < 0.0:
            raise ValueError, "Cutoff energy inelastic (%s) must be greater or equal to 0.0" \
                    % energy
        self._props['cutoff energy inelastic'] = energy

    @property
    def cutoff_energy_bremsstrahlung_eV(self):
        """
        Cutoff energy for Bremsstrahlung emission (in eV).
        """
        return self._props['cutoff energy bremsstrahlung']

    @cutoff_energy_bremsstrahlung_eV.setter
    def cutoff_energy_bremsstrahlung_eV(self, energy):
        if energy < 0.0:
            raise ValueError, "Cutoff energy Bremsstrahlung (%s) must be greater or equal to 0.0" \
                    % energy
        self._props['cutoff energy bremsstrahlung'] = energy

XMLIO.register('{http://pymontecarlo.sf.net/penelope}material', Material)
XMLIO.register_loader('pymontecarlo.input.penelope.material.Material', Material)

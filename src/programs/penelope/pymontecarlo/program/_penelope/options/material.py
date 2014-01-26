#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- PENELOPE material definition
================================================================================

.. module:: material
   :synopsis: PENELOPE material definition

.. inheritance-diagram:: pymontecarlo.program._penelope.options.material

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from collections import namedtuple
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.options.material import Material as _Material

# Globals and constants variables.
from pymontecarlo.options.particle import PARTICLES
from pymontecarlo.options.collision import COLLISIONS

ElasticScattering = namedtuple('ElasticScattering', ['c1', 'c2'])

class InteractionForcing(object):

    def __init__(self, particle, collision, forcer=-1, weight=(0.1, 1.0)):
        """
        Creates a new interaction forcing.

        :arg particle: type of particle
        :type particle: :class:`_Particle`

        :arg collision: type of collisions
        :type collision: :class:`_Collision`

        :arg forcer: forcing factor (``default=-1``)

        :arg weight: weight window where interaction is applied.
            The weight is a :class:`tuple` of the low and high limits
            (``default=(0.1, 1.0)``)
        """
        if particle not in PARTICLES:
            raise ValueError('Unknown particle: %s' % particle)
        self._particle = particle

        if collision not in COLLISIONS:
            raise ValueError('Unknown collision: %s' % collision)
        self._collision = collision

        if forcer == 0.0:
            raise ValueError('Forcer cannot be 0.0')
        self._forcer = forcer

        if weight[0] < 0.0 or weight[0] > 1.0 or \
                weight[1] < 0.0 or weight[1] > 1.0:
            raise ValueError('Weight must be between [0.0, 1.0]')
        self._weight = tuple(weight)

    def __repr__(self):
        return '<%s(%s, %s, forcer=%i, weight=(%f, %f))>' % \
            (self.__class__.__name__, str(self.particle), str(self.collision),
             self.forcer, self.weight.low, self.weight.high)

    def __eq__(self, other):
        return self.particle is other.particle and \
                    self.collision is other.collision

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(('interactionforcing', self.particle, self.collision))

    @property
    def particle(self):
        """
        Type of particles.
        """
        return self._particle

    @property
    def collision(self):
        """
        Type of collisions.
        """
        return self._collision

    @property
    def forcer(self):
        """
        Forcing factor.
        """
        return self._forcer

    @property
    def weight(self):
        """
        Weight window where interaction is applied.
        """
        return self._weight

class Material(_Material):

    def __init__(self, composition, name=None, density_kg_m3=None, absorption_energy_eV=None,
                 elastic_scattering=(0.0, 0.0),
                 cutoff_energy_inelastic_eV=50.0, cutoff_energy_bremsstrahlung_eV=50.0,
                 interaction_forcings=None, maximum_step_length_m=1e20):
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

        :arg elastic_scattering: elastic scattering coefficients.
            They can either be specified as a :class:`tuple`: ``(C1, C2)`` or
            as a single :class:`float` value, where ``C1=C2``.
            The value of C1 or C2 must be between 0.0 and 0.2 inclusively.
        :type elastic_scattering: :class:`tuple` or :class:`float`

        :arg cutoff_energy_inelastic_eV: cutoff energy for inelastic collisions
            (in eV).

        :arg cutoff_energy_bremsstrahlung_eV: cutoff energy for Bremsstrahlung
            emission (in eV).

        :arg interaction_forcings: interaction forcing(s)

        :arg maximum_step_length_m: maximum length of an electron trajectory
        """
        _Material.__init__(self, composition, name, density_kg_m3, absorption_energy_eV)

        elastic_scattering = ElasticScattering(*elastic_scattering)
        if elastic_scattering.c1 < 0.0 or elastic_scattering.c1 > 0.2:
            raise ValueError('C1 must be between [0.0, 0.2]')
        if elastic_scattering.c2 < 0.0 or elastic_scattering.c2 > 0.2:
            raise ValueError('C2 must be between [0.0, 0.2]')
        self._elastic_scattering = elastic_scattering

        if cutoff_energy_inelastic_eV < 0.0:
            raise ValueError('Cutoff energy for inelastic collisions must be greater or equal to 0.0')
        self._cutoff_energy_inelastic_eV = cutoff_energy_inelastic_eV

        if cutoff_energy_inelastic_eV < 0.0:
            raise ValueError('Cutoff energy for Bremsstrahlung emission must be greater or equal to 0.0')
        self._cutoff_energy_bremsstrahlung_eV = cutoff_energy_bremsstrahlung_eV

        if interaction_forcings is None:
            interaction_forcings = set()
        self._interaction_forcings = frozenset(interaction_forcings)

        if maximum_step_length_m < 0.0:
            raise ValueError("Length must be greater than 0.0")
        if maximum_step_length_m > 1e20:
            warnings.warn('Maximum step length set to maximum value: 1e20')
            maximum_step_length_m = 1e20
        self._maximum_step_length_m = maximum_step_length_m

    @classmethod
    def pure(cls, z, absorption_energy_eV=None, elastic_scattering=(0.0, 0.0),
             cutoff_energy_inelastic_eV=50.0, cutoff_energy_bremsstrahlung_eV=50.0,
             interaction_forcings=None, maximum_step_length_m=1e20):
        mat = _Material.pure(z, absorption_energy_eV)
        return cls(mat.composition, mat.name, mat.density_kg_m3, mat.absorption_energy_eV,
                   elastic_scattering, cutoff_energy_inelastic_eV, cutoff_energy_bremsstrahlung_eV,
                   interaction_forcings, maximum_step_length_m)

    def __repr__(self):
        return '<Material(name=%s, composition=%s, density=%s kg/m3, abs_electron=%s eV, abs_photon=%s eV, abs_positron=%s eV, elastic_scattering=%s, cutoff_inelastic=%s eV, cutoff_bremsstrahlung=%s eV, interaction_forcings=%s, maximum_step_length=%s m)>' % \
            (self.name, self.composition, self.density_kg_m3,
             self.absorption_energy_electron_eV, self.absorption_energy_photon_eV,
             self.absorption_energy_positron_eV,
             self.elastic_scattering,
             self.cutoff_energy_inelastic_eV, self.cutoff_energy_bremsstrahlung_eV,
             self.interaction_forcings, self.maximum_step_length_m)

    @property
    def elastic_scattering(self):
        """
        Elastic scattering coefficients.
        """
        return self._elastic_scattering

    @property
    def cutoff_energy_inelastic_eV(self):
        """
        Cutoff energy for inelastic collisions (in eV).
        """
        return self._cutoff_energy_inelastic_eV

    @property
    def cutoff_energy_bremsstrahlung_eV(self):
        """
        Cutoff energy for Bremsstrahlung emission (in eV).
        """
        return self._cutoff_energy_bremsstrahlung_eV

    @property
    def interaction_forcings(self):
        """
        Interaction forcing(s).
        """
        return self._interaction_forcings

    @property
    def maximum_step_length_m(self):
        """
        Maximum length of an electron trajectory (in meters).
        """
        return self._maximum_step_length_m


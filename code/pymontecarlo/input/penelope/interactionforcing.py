#!/usr/bin/env python
"""
================================================================================
:mod:`interactionforcing` -- Interaction forcing
================================================================================

.. module:: interactionforcing
   :synopsis: Interaction forcing

.. inheritance-diagram:: pymontecarlo.input.penelope.interactionforcing

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
from pymontecarlo.input.penelope.option import Option
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.
ELECTRON = 1
PHOTON = 2
POSITRON = 3

class Collisions(object):
    def __init__(self, particle):
        """
        Structure for the particle_type of collisions for each primary particle.
    
        :arg particle: particle_type of particle (use :const:`ELECTRON`, 
            :const:`PHOTON` or :const:`POSITRON`)
        :type particle: :class:`int`
    
        **Examples**::
    
          >>> collision = Collisions(ELECTRON).HARD_ELASTIC_COLLISION
          >>> print collision
          >>> 2
          
        """
        if particle == ELECTRON:
            self.ARTIFICIAL_SOFT_EVENT = 1
            self.HARD_ELASTIC_COLLISION = 2
            self.HARD_INELASTIC_COLLISION = 3
            self.HARD_BREMSSTRAHLUNG_EMISSION = 4
            self.INNERSHELL_IMPACT_IONISATION = 5
            self.DELTA_INTERACTION = 7
            self.AUXILIARY_INTERACTION = 8
        elif particle == PHOTON:
            self.COHERENT_RAYLEIGH_SCATTERING = 1
            self.INCOHERENT_COMPTON_SCATTERING = 2
            self.PHOTOELECTRIC_ABSORPTION = 3
            self.ELECTRON_POSITRON_PAIR_PRODUCTION = 4
            self.DELTA_INTERACTION = 7
            self.AUXILIARY_INTERACTION = 8
        elif particle == POSITRON:
            self.ARTIFICIAL_SOFT_EVENT = 1
            self.HARD_ELASTIC_COLLISION = 2
            self.HARD_INELASTIC_COLLISION = 3
            self.HARD_BREMSSTRAHLUNG_EMISSION = 4
            self.INNERSHELL_IMPACT_IONISATION = 5
            self.ANNIHILATION = 6
            self.DELTA_INTERACTION = 7
            self.AUXILIARY_INTERACTION = 8

    @property
    def possible_collisions(self):
        """
        Returns all the possible collisions for the primary particle.
    
        :rtype: :class:`dict`
        """
        variables = vars(self).copy()
        return variables

class InteractionForcing(Option):
    def __init__(self, particle, collision, forcer= -1, weight=(0.1, 1.0)):
        """
        Creates a new interaction forcing.
    
        :arg particle: type of particle (use :const:`ELECTRON`, :const:`PHOTON` 
            or :const:`POSITRON`)
        :type particle: :class:`int`
    
        :arg collision: type of collisions (see :class:`Collisions`)
        :type collision: :class:`int`
    
        :arg forcer: forcing factor (``default=-1``)
    
        :arg weight: weight window where interaction is applied. 
            The weight is a :class:`tuple` of the low and high limits 
            (``default=(0.1, 1.0)``)
        """
        Option.__init__(self)

        self.particle = particle
        self.collision = collision
        self.forcer = forcer
        self.weight = weight

    def __cmp__(self, other):
        """
        Comparison between two :class:`InteractionForcing` using the function 
        :func:`cmp(x, y)`
    
        The *particle* and *collision* are compared in this order of importance.
        If they are all equal, the two :class:`InteractionForcing` are 
        defined as equal.
        """
        if self.particle > other.particle:
            return 1
        elif self.particle < other.particle:
            return -1
        else:
            if self.collision > other.collision:
                return 1
            elif self.collision < other.collision:
                return -1
            else:
                return 0

    def __hash__(self):
        return hash((self.particle, self.collision))

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        particle = int(element.get('particle'))
        collision = int(element.get('collision'))
        forcer = float(element.get('forcer'))
        weight = (float(element.get('weightMin')), float(element.get('weightMax')))

        return cls(particle, collision, forcer, weight)

    def __savexml__(self, element, *args, **kwargs):
        element.set('particle', str(self.particle))
        element.set('collision', str(self.collision))
        element.set('forcer', str(self.forcer))
        element.set('weightMin', str(self.weight[0]))
        element.set('weightMax', str(self.weight[1]))

    @property
    def particle(self):
        """
        Type of particle.
        The particle can either be a :const:`ELECTRON`, :const:`PHOTON` 
        or :const:`POSITRON`.
        """
        return self._props['particle']

    @particle.setter
    def particle(self, particle):
        if not particle in [ELECTRON, PHOTON, POSITRON]:
            raise ValueError, "Incorrect particle type (%s)." % particle
        self._props['particle'] = particle

    @property
    def collision(self):
        """
        Type of collision.
        A value between 1 and 8.
        See :class:`.Collisions` for the definitions.
        """
        return self._props['collision']

    @collision.setter
    def collision(self, collision):
        if collision < 1 or collision > 8:
            raise ValueError, "Incorrect collision type (%s)." % collision
        self._props['collision'] = collision

    @property
    def forcer(self):
        """
        Forcing value.
        If negative the forcing value is adjusted based on the interaction volume.
        """
        return self._props['forcer']

    @forcer.setter
    def forcer(self, forcer):
        if forcer == 0.0:
            raise ValueError, "Forcer (%s) cannot be equal to zero." % forcer
        self._props['forcer'] = forcer

    @property
    def weight(self):
        """
        The weight window where interaction is applied.
        The low and upper limits must be between 0.0 and 1.0.
        """
        return self._props['weight']

    @weight.setter
    def weight(self, weight):
        low, high = weight

        if low < 0 or low > 1:
            raise ValueError, "Weight low limit (%s) must be between [0, 1]." % low
        if high < 0 or high > 1:
            raise ValueError, "Weight upper limit (%s) must be between [0, 1]." % high

        self._props['weight'] = min(low, high), max(low, high)

XMLIO.register('{http://pymontecarlo.sf.net/input/penelope}interactionForcing', InteractionForcing)
XMLIO.register_loader('pymontecarlo.input.penelope.interactionforcing.InteractionForcing', InteractionForcing)

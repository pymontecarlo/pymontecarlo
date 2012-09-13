#!/usr/bin/env python
"""
================================================================================
:mod:`interactionforcing` -- Interaction forcing
================================================================================

.. module:: interactionforcing
   :synopsis: Interaction forcing

.. inheritance-diagram:: pymontecarlo.program.penelope.input.interactionforcing

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
from pymontecarlo.input.option import Option
from pymontecarlo.input.particle import PARTICLES
from pymontecarlo.input.collision import COLLISIONS

from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

class InteractionForcing(Option):
    def __init__(self, particle, collision, forcer= -1, weight=(0.1, 1.0)):
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
        Option.__init__(self)

        self.particle = particle
        self.collision = collision
        self.forcer = forcer
        self.weight = weight

    def __eq__(self, other):
        return self.particle is other.particle and \
                    self.collision is other.collision
    
    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(('interactionforcing', self.particle, self.collision))

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        particles = list(PARTICLES)
        particles = dict(zip(map(str, particles), particles))
        particle = particles[element.get('particle')]

        collisions = list(COLLISIONS)
        collisions = dict(zip(map(str, collisions), collisions))
        collision = collisions[element.get('collision')]

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
        """
        return self._props['particle']

    @particle.setter
    def particle(self, particle):
        if particle not in PARTICLES:
            raise ValueError, 'Particle (%i) must be %s' % (particle, PARTICLES)
        self._props['particle'] = particle

    @property
    def collision(self):
        """
        Type of collision.
        """
        return self._props['collision']

    @collision.setter
    def collision(self, collision):
        if collision not in COLLISIONS:
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

XMLIO.register('{http://pymontecarlo.sf.net/penelope}interactionForcing', InteractionForcing)

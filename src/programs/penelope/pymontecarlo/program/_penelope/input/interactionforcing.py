#!/usr/bin/env python
"""
================================================================================
:mod:`interactionforcing` -- Interaction forcing
================================================================================

.. module:: interactionforcing
   :synopsis: Interaction forcing

.. inheritance-diagram:: pymontecarlo.program._penelope.input.interactionforcing

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
from pymontecarlo.input.particle import PARTICLES, ParticleType
from pymontecarlo.input.collision import COLLISIONS, CollisionType
from pymontecarlo.input.bound import bound
from pymontecarlo.input.parameter import ParameterizedMetaClass, Parameter, EnumValidator, SimpleValidator, CastValidator
from pymontecarlo.input.xmlmapper import mapper, ParameterizedAttribute, ParameterizedElement, PythonType, UserType

# Globals and constants variables.

_forcer_validator = SimpleValidator(lambda forcer: forcer != 0.0)
_weight_validator = SimpleValidator(lambda x: 0 <= x.low <= 1 and \
                                              0 <= x.high <= 1.0)

class InteractionForcing(object):

    __metaclass__ = ParameterizedMetaClass

    particle = Parameter(EnumValidator(PARTICLES),
                         "Type of particles (see :mod:`.particle`)")
    collision = Parameter(EnumValidator(COLLISIONS),
                         "Type of collisions (see :mod:`.collision`)")
    forcer = Parameter(_forcer_validator, "Forcing factor")
    weight = Parameter([CastValidator(bound), _weight_validator],
                       "Weight window where interaction is applied. The low and upper limits must be between 0.0 and 1.0.")

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
        self.particle = particle
        self.collision = collision
        self.forcer = forcer
        self.weight = weight

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

mapper.register(InteractionForcing, '{http://pymontecarlo.sf.net/penelope}interactionForcing',
                ParameterizedAttribute('particle', ParticleType()),
                ParameterizedAttribute('collision', CollisionType()),
                ParameterizedAttribute('forcer', PythonType(int)),
                ParameterizedElement('weight', UserType(bound)))

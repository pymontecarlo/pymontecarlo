#!/usr/bin/env python
"""
================================================================================
:mod:`measurement` -- Measurement
================================================================================

.. module:: measurement
   :synopsis: Measurement

.. inheritance-diagram:: pymontecarlo.quant.input.measurement

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter

# Third party modules.
from lxml.etree import Element
from pymontecarlo.input.options import Options #@UnusedImport

# Local modules.
from pymontecarlo.input.material import pure

from pymontecarlo.quant.input.rule import ElementByDifferenceRule

import pymontecarlo.util.element_properties as ep
from pymontecarlo.util.xmlutil import XMLIO, objectxml

# Globals and constants variables.

class Measurement(objectxml):

    def __init__(self, options, unknown_body, detector_key):
        """
        Creates a new measurement.
        
        :arg options: simulation options corresponding to this measurement
        :type options: :class:`.Options`
        
        :arg unknown_body: object of the body from which the k-ratio 
            measurements were performed from.
        :type unknown_body: :class:`.Body`
        
        :arg detector_key: key of the detector from which the k-ratio 
            measurements were recorded from.
        :type detector_key: :class:`str`
        
        :raise: :exc:`ValueError` if the specified body is not part of the
            simulation options
        :raise: :exc:`ValueError` if the specified detector is not part of the
            simulation options
        """
        self._options = options

        if unknown_body not in self.options.geometry.get_bodies():
            raise ValueError, 'Body is not part of the geometry'
        self._unknown_body = unknown_body

        if detector_key not in self.options.detectors:
            raise ValueError, 'Detector is not part of the options'
        self._detector_key = detector_key

        self._transitions = {}
        self._kratios = {}
        self._standards = {}
        self._rules = {}

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        # options
        parent = element.find('options')
        if parent is None:
            raise IOError, 'No options defined.'
        child = list(parent)[0]
        ops = XMLIO.from_xml(child)

        # unknown body
        bodies = list(ops.geometry.get_bodies())
        indexes = map(attrgetter('_index'), bodies)
        bodies_lookup = dict(zip(indexes, bodies))

        index = int(element.get('body'))
        unknown_body = bodies_lookup[index]

        # detector key
        detector_key = element.get('detector')

        measurement = cls(ops, unknown_body, detector_key)

        # k-ratios
        parent = element.find('kratios')
        if parent is not None:
            for child in parent:
                val = float(child.get('val'))
                unc = float(child.get('unc', 0.0))

                grandchild = child.find('transition')
                if grandchild is None:
                    raise IOError, 'kratio does not have a transition'
                transition = XMLIO.from_xml(list(grandchild)[0])

                grandchild = child.find('standard')
                if grandchild is None:
                    raise IOError, 'kratio does not have a standard'
                standard = XMLIO.from_xml(list(grandchild)[0])

                measurement.add_kratio(transition, val, unc, standard)

        # rules
        parent = element.find('rules')
        if parent is not None:
            for child in parent:
                rule = XMLIO.from_xml(child)
                measurement.add_rule(rule)

        return measurement

    def __savexml__(self, element, *args, **kwargs):
        # options
        child = Element('options')
        child.append(self.options.to_xml())
        element.append(child)

        # k-ratios
        child = Element('kratios')

        for z, transition in self._transitions.iteritems():
            val, unc = self._kratios[z]
            standard = self._standards[z]

            grandchild = Element('kratio')
            grandchild.set('val', str(val))
            grandchild.set('unc', str(unc))

            grandgrandchild = Element('transition')
            grandgrandchild.append(transition.to_xml())
            grandchild.append(grandgrandchild)

            grandgrandchild = Element('standard')
            grandgrandchild.append(standard.to_xml())
            grandchild.append(grandgrandchild)

            child.append(grandchild)

        element.append(child)

        # rules
        child = Element('rules')

        for rule in self._rules.itervalues():
            child.append(rule.to_xml())

        element.append(child)

        element.set('body', str(self.unknown_body._index))
        element.set('detector', self.detector_key)

    @property
    def options(self):
        """
        Simulation options.
        """
        return self._options

    @property
    def unknown_body(self):
        """
        Body from which the k-ratio were measured.
        """
        return self._unknown_body

    @property
    def detector_key(self):
        """
        Photon intensity detector from which the k-ratio were measured.
        """
        return self._detector_key

    def add_kratio(self, transition, val, unc=0.0, standard=None):
        """
        Adds a k-ratio to this measurement.
        
        :arg transition: transition or set of transition for this k-ratio
        :type transition: :class:`.Transition` or :class:`.transitionset`
        
        :arg val: k-ratio value
        :type val: :class:`float`
        
        :arg unc: uncertainty on the k-ratio value (default: 0.0)
        :type unc: :class:`float`
        
        :arg standard: material of the standard
        :type standard: :class:`.Material`
        
        :raise: :exc:`ValueError` if a k-ratio or rule is already defined for
            the atomic number of the specified transition
        """
        z = transition.z

        if z in self._transitions:
            raise ValueError, 'A k-ratio is already defined for element: %s' % ep.symbol(z)
        if z in self._rules:
            raise ValueError, 'A rule is already defined for element: %s' % ep.symbol(z)
        if val < 0.0:
            raise ValueError, 'k-ratio value must be greater than 0.0'
        if unc < 0.0:
            raise ValueError, 'k-ratio uncertainty must be greater than 0.0'

        if standard is None:
            standard = pure(z)

        self._transitions[z] = transition
        self._kratios[z] = (val, unc)
        self._standards[z] = standard

    def add_rule(self, rule):
        """
        Adds a rule to this measurement.
        
        :arg rule: rule object
        """
        z = rule.z

        if z in self._rules:
            raise ValueError, 'A rule is already defined for element: %s' % ep.symbol(z)
        if z in self._transitions:
            raise ValueError, 'A k-ratio is already defined for element: %s' % ep.symbol(z)

        # Ensure that there is only one ElementByDifference rule
        diff_rules = any(map(lambda rule: isinstance(rule, ElementByDifferenceRule),
                             self._rules.values()))
        if diff_rules and isinstance(rule, ElementByDifferenceRule):
            raise ValueError, 'A ElementByDifferenceRule was already added'

        self._rules[z] = rule

    def remove_kratio(self, z):
        """
        Removes a k-ratio from this measurement.
        
        :arg z: atomic number of the k-ratio to be removed
        """
        self._transitions.pop(z)
        self._kratios.pop(z)
        self._standards.pop(z)

    def remove_rule(self, z):
        """
        Removes a rule from this measurement.
        
        :arg z: atomic number of the rule to be removed
        """
        self._rules.pop(z)

    def has_kratio(self, z):
        """
        Whether a k-ratio is defined for this atomic number.
        
        :arg z: atomic number
        """
        return z in self._transitions

    def has_rule(self, z):
        """
        Whether a rule is defined for this atomic number.
        
        :arg z: atomic number
        """
        return z in self._rules

    def get_transitions(self):
        """
        Returns a :class:`list` of all transitions where a k-ratio has been
        defined.
        """
        return self._transitions.values()

    def get_kratios(self):
        """
        Returns a :class:`dict` where the keys are atomic numbers and the values 
        are tuples of the k-ratios and their uncertainties.
        """
        return dict(self._kratios) # copy

    def get_standards(self):
        """
        Returns a :class:`dict` where the keys are atomic numbers and the values
        are the material objects of the standards
        """
        return dict(self._standards) # copy

    def get_rules(self):
        """
        Returns a :class:`list` of all the defined rules.
        """
        return self._rules.values()

XMLIO.register('{http://pymontecarlo.sf.net}measurement', Measurement)

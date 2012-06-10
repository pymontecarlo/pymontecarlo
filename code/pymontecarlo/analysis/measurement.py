#!/usr/bin/env python
"""
================================================================================
:mod:`measurement` -- Measurement
================================================================================

.. module:: measurement
   :synopsis: Measurement

.. inheritance-diagram:: pymontecarlo.analysis.measurement

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.input.material import pure
from pymontecarlo.analysis.rule import ElementByDifference
import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

class Measurement(object):

    def __init__(self, options, unknown_body, detector_key):
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

        self._element_by_difference = None

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

    def add_kratio(self, transition, val, standard=None):
        z = transition.z

        if z in self._transitions:
            raise ValueError, 'A k-ratio is already defined for element: %s' % ep.symbol(z)
        if z in self._rules:
            raise ValueError, 'A rule is already defined for element: %s' % ep.symbol(z)
        if val < 0.0:
            raise ValueError, 'k-ratio value must be greater than 0.0'

        if standard is None:
            standard = pure(z)

        self._transitions[z] = transition
        self._kratios[z] = val
        self._standards[z] = standard

    def add_rule(self, rule):
        z = rule.z

        if z in self._rules:
            raise ValueError, 'A rule is already defined for element: %s' % ep.symbol(z)
        if z in self._transitions:
            raise ValueError, 'A k-ratio is already defined for element: %s' % ep.symbol(z)

        # Ensure that there is only one ElementByDifference rule
        diff_rules = any(map(lambda rule: isinstance(rule, ElementByDifference),
                             self._rules.values()))
        if diff_rules and isinstance(rule, ElementByDifference):
            raise ValueError, 'A rule ElementByDifference was already added'

        self._rules[z] = rule

    def remove_kratio(self, z):
        self._transitions.pop(z)
        self._kratios.pop(z)
        self._standards.pop(z)

    def remove_rule(self, z):
        self._rules.pop(z)

    def has_kratio(self, z):
        return z in self._transitions

    def has_rule(self, z):
        return z in self._rules

    def get_transitions(self):
        return self._transitions.values()

    def get_kratios(self):
        return dict(self._kratios) # copy

    def get_standards(self):
        return dict(self._standards) # copy

    def get_rules(self):
        return self._rules.values()


#!/usr/bin/env python
"""
================================================================================
:mod:`helper` -- Small routines to help change values in options
================================================================================

.. module:: helper
   :synopsis: Small routines to help change values in options

.. inheritance-diagram:: helper

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import itemgetter

# Third party modules.

# Local modules.
from pymontecarlo.input.detector import \
   (_EnergyDetector, _ElectronRangeDetector, _PhotonRangeDetector,
     _TransitionDetector)
from pymontecarlo.util.relaxation_data import RelaxationData

# Globals and constants variables.

def replace_material(options, old_material, new_material):
    """
    Replaces all occurrences of *old_material* with *new_material* in the 
    options.
    
    :arg options: options
    :arg old_material: material to be replaced
    :arg new_material: new material
    
    :return: number of occurrences
    """
    count = 0

    for body in options.geometry.get_bodies():
        if body.material is old_material:
            body.material = new_material
            count += 1

    return count

def ensure_emax(options, emax=None):
    """
    Ensures that the beam energy and all upper energy limits of the detectors
    is set to *emax*.
    If *emax* is ``None``, the beam energy from the options is used.
    
    :arg options: options
    :arg emax: maximum energy in eV
    
    :return: *emax*
    """
    if emax is None:
        emax = options.beam.energy

    options.beam.energy = emax

    for detector in options.detectors.values():
        if isinstance(detector, _EnergyDetector):
            detector.limits = (detector.limits[0], emax)

    return emax

def check_transitions(options):
    """
    Checks that the photon transitions specified in all detectors are valid:
    
      * They correspond to a material inside the geometry
      * Their energy is less than the beam energy
    
    :raise: `ValueError` if the two criteria are not met
    """
    emax = options.beam.energy
    relaxation = RelaxationData()

    # Find all possible atomic numbers
    zs = []
    for material in options.geometry.get_materials():
        zs += map(itemgetter[0], material.composition)

    # Check PhotonTransitionDetector
    for name, detector in options.detectors.iteritems():
        if isinstance(detector, _TransitionDetector):
            transition = detector.transion

            if transition.z not in zs:
                raise ValueError, \
                    "Detector '%s': No material with atomic number %i." % \
                        (name, transition.z)

            energy = relaxation.energy(transition=transition)
            if energy > emax:
                raise ValueError, \
                    "Detector '%s': Transition energy (%s) is larger than beam energy (%s)." % \
                        (name, energy, emax)

def adjust_range(options, safety_factor=1.5):
    """
    Adjusts the photon and electron ranges of all the detectors based on the
    
    """
    energy = options.beam.energy

    for detector in options.detectors.values():
        if isinstance(detector, _ElectronRangeDetector):
            pass
        elif isinstance(detector, _PhotonRangeDetector):
            transition = detector.transition
            pass

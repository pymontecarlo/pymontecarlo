#!/usr/bin/env python
"""
================================================================================
:mod:`callback` -- Callbacks for PENELOPE simulation
================================================================================

.. module:: callback
   :synopsis: Callbacks for PENELOPE simulation

.. inheritance-diagram:: penelopetools.lib.callback

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
import logging

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.util.histogram import SumHistogram
from pymontecarlo.lib.penelope.wrapper import track

# Globals and constants variables.

class _Callback:
    def __init__(self):
        pass

    def __iadd__(self, other):
        return self

    def trajectory_end(self, n):
        return True

    def backscattered_electron(self, n):
        pass

    def transmitted_electron(self, n):
        pass

    def absorbed_electron(self, n):
        pass

    def exit_photon(self, n):
        pass

    def absorbed_photon(self, n):
        pass

    def generated_electron(self, n):
        pass

    def generated_photon(self, n):
        pass

    def knock(self, n, icol, de):
        pass

class DebugCallback(_Callback):
    def trajectory_end(self, n):
        logging.debug("Trajectory end: n=%s", n)
        return True

    def backscattered_electron(self, n):
        logging.debug("Backscattered electron: n=%s", n)

    def transmitted_electron(self, n):
        logging.debug("Transmitted electron: n=%s", n)

    def absorbed_electron(self, n):
        logging.debug("Absorbed electron: n=%s", n)

    def exit_photon(self, n):
        logging.debug("Exit photon: n=%s", n)

    def absorbed_photon(self, n):
        logging.debug("Absorbed photon: n=%s", n)

    def generated_electron(self, n):
        logging.debug("Generated electron: n=%s", n)

    def generated_photon(self, n):
        logging.debug("Generated photon: n=%s", n)

    def knock(self, n, icol, de):
        logging.debug("Knock: n=%s, icol=%s, de=%s", n, icol, de)

class ParticleCounterCallback(_Callback):
    def __init__(self):
        # Counter for primary electrons
        #   row 0: value, row 1: value^2
        #   col 0: backscattered, col 1: transmitted, col 2: absorbed
        self.primary_electron = np.zeros((2, 3))
        self._dprimary_electron = np.zeros(3)

        # Counter for secondary electrons
        #   row 0: value, row 1: value^2
        #   col 0: backscattered, col 1: transmitted, col 2: absorbed
        self.secondary_electron = np.zeros((2, 3))
        self._dsecondary_electron = np.zeros(3)

    def __iadd__(self, other):
        self.primary_electron += other.primary_electron
        self.secondary_electron += other.secondary_electron

        return self

    def trajectory_end(self, n):
        self.primary_electron[0] += self._dprimary_electron
        self.primary_electron[1] += self._dprimary_electron ** 2
        self._dprimary_electron[:] = 0.0

        self.secondary_electron[0] += self._dsecondary_electron
        self.secondary_electron[1] += self._dsecondary_electron ** 2
        self._dsecondary_electron[:] = 0.0

        return True

    def backscattered_electron(self, n):
        weight = track.weight
        if track.labels[0] == 1 :
            self._dprimary_electron[0] += weight
        else:
            self._dsecondary_electron[0] += weight

    def transmitted_electron(self, n):
        weight = track.weight
        if track.labels[0] == 1 :
            self._dprimary_electron[1] += weight
        else:
            self._dsecondary_electron[1] += weight

    def absorbed_electron(self, n):
        weight = track.weight
        if track.labels[0] == 1 :
            self._dprimary_electron[2] += weight
        else:
            self._dsecondary_electron[2] += weight

class EnergyDepositedCallback(_Callback):
    def __init__(self, body=1):
        """
        Callback to collect energy deposited.
        
        :arg body: number of bodies in the geometry
        """
        # Counter for energy deposited in bodies
        #   col i: energy deposited in body i
        self.deposited_energy = np.zeros(body)

    def __iadd__(self, other):
        self.deposited_energy += other.deposited_energy

        return self

    def absorbed_electron(self, n):
        ibody = track.body
        energy = track.energy
        weight = track.weight
        self.deposited_energy[ibody] += energy * weight

    def knock(self, n, icol, de):
        ibody = track.body
        weight = track.weight
        self.deposited_energy[ibody] += de * weight

class ElectronEnergyDistributionCallback(_Callback):
    def __init__(self, energy_min, energy_max, nbins):
        """
        Records energy distribution of backscattered and transmitted electrons.
        
        :arg energy_min: minimum energy of the distribution (eV)
        :arg energy_max: maximum energy of the distribution (eV)
        :arg nbins: number of bins
        """
        step = (energy_max - energy_min) / nbins
        bins = np.arange(energy_min, energy_max, step)

        self.backscattered = SumHistogram(bins)
        self._dbackscattered = SumHistogram(bins)

        self.transmitted = SumHistogram(bins)
        self._dtransmitted = SumHistogram(bins)

    def __iadd__(self, other):
        self.backscattered += other.backscattered
        self.transmitted += other.transmitted
        return self

    def trajectory_end(self, n):
        self.backscattered += self._dbackscattered
        self._dbackscattered.clear()

        self.transmitted += self._dtransmitted
        self._dtransmitted.clear()

        return True

    def backscattered_electron(self, n):
        energy = track.energy
        weight = track.weight
        self._dbackscattered.add(energy, weight)

    def transmitted_electron(self, n):
        energy = track.energy
        weight = track.weight
        self._dtransmitted.add(energy, weight)

class ElectronPolarDistributionCallback(_Callback):
    def __init__(self, theta_min, theta_max, nbins):
        step = (theta_max - theta_min) / nbins
        bins = np.arange(theta_min, theta_max, step)

        self.backscattered = SumHistogram(bins)
        self._dbackscattered = SumHistogram(bins)

        self.transmitted = SumHistogram(bins)
        self._dtransmitted = SumHistogram(bins)

    def __iadd__(self, other):
        self.backscattered += other.backscattered
        self.transmitted += other.transmitted
        return self

    def trajectory_end(self, n):
        self.backscattered += self._dbackscattered
        self._dbackscattered.clear()

        self.transmitted += self._dtransmitted
        self._dtransmitted.clear()

        return True

    def backscattered_electron(self, n):
        theta = math.acos(track.direction[2])
        weight = track.weight
        self._dbackscattered.add(theta, weight)

    def transmitted_electron(self, n):
        theta = math.acos(track.direction[2])
        weight = track.weight
        self._dtransmitted.add(theta, weight)

class PhotonEnergyDistributionCallback(_Callback):
    def __init__(self, theta_min, theta_max, energy_min, energy_max, energy_nbins):
        self._theta_min = theta_min
        self._theta_max = theta_max

        step = (energy_max - energy_min) / energy_nbins
        bins = np.arange(energy_min, energy_max, step)

        self.detector = SumHistogram(bins)
        self._ddetector = SumHistogram(bins)

    def __iadd__(self, other):
        self.detector += other.detector
        return self

    def trajectory_end(self, n):
        self.detector += self._ddetector
        self._ddetector.clear()

        return True

    def exit_photon(self, n):
        theta = math.acos(track.direction[2])
        if theta >= self._theta_min and theta <= self._theta_max:
            energy = track.energy
            weight = track.weight
            self._ddetector.add(energy, weight)

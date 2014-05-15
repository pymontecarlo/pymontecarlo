#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- Simulation results
================================================================================

.. module:: result
   :synopsis: Simulation results

.. inheritance-diagram:: pymontecarlo.output.result

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import bisect
from math import sqrt
from collections import Iterable, Sized

# Third party modules.
import numpy as np

from pyxray.transition import from_string, transitionset

# Local modules.

# Globals and constants variables.
from pymontecarlo.options.particle import PARTICLES
from pymontecarlo.options.collision import COLLISIONS

class _Result(object):
    """
    Base class of all results.
    A result is a read-only class where results of a detector are stored.
    """

class PhotonKey(object):

    PRIMARY = 'P'
    CHARACTERISTIC_FLUORESCENCE = 'C'
    BREMSSTRAHLUNG_FLUORESCENCE = 'B'
    FLUORESCENCE = 'F'
    TOTAL = 'T'

    P = PRIMARY
    C = CHARACTERISTIC_FLUORESCENCE
    B = BREMSSTRAHLUNG_FLUORESCENCE
    F = FLUORESCENCE
    T = TOTAL

    def __init__(self, transition, absorption, flag):
        self._transition = transition
        self._absorption = absorption
        self._flag = flag

        # Generate __str__
        key = self._flag + 'E' if absorption else 'G'
        self._str = str(self.transition) + ' ' + key

    def __str__(self):
        return self._str

    def __hash__(self):
        return hash((self.__class__, self._transition, self._absorption, self._flag))

    def __eq__(self, other):
        return self._transition == other.transition and \
            self._absorption == other._absorption and \
            self._flag == other._flag

    def is_generated(self):
        return not self._absorption

    def is_emitted(self):
        return self._absorption

    @property
    def transition(self):
        return self._transition

    @property
    def flag(self):
        return self._flag

def _create_photon_keys(results, transition, absorption, primary,
                        characteristic_fluorescence, bremsstrahlung_fluorescence):
    # Check for total photon key
    if primary and characteristic_fluorescence and bremsstrahlung_fluorescence:
        key = PhotonKey(transition, absorption, PhotonKey.T)
        if key in results:
            return [key]

    # Check for fluorescence key
    elif not primary and characteristic_fluorescence and bremsstrahlung_fluorescence:
        key = PhotonKey(transition, absorption, PhotonKey.F)
        if key in results:
            return [key]

    # All other cases
    keys = []

    if primary:
        key = PhotonKey(transition, absorption, PhotonKey.P)
        if key in results:
            keys.append(key)
    if characteristic_fluorescence:
        key = PhotonKey(transition, absorption, PhotonKey.C)
        if key in results:
            keys.append(key)
    if bremsstrahlung_fluorescence:
        key = PhotonKey(transition, absorption, PhotonKey.B)
        if key in results:
            keys.append(key)

    return keys

class PhotonIntensityResult(_Result):

    def __init__(self, intensities=None):
        """
        Creates a new result to store photon intensities.

        :arg intensities: :class:`dict` containing the intensities.
            The keys should be :class:`.PhotonKey` and the values a tuple or
            array of length 2 containing the intensity and its uncertainty
        """
        _Result.__init__(self)

        if intensities is None:
            intensities = {}

        self._intensities = {}
        for key, intensity in intensities.items():
            self._intensities[key] = np.array([intensity])

    def __contains__(self, transition):
        return self.has_intensity(transition)

    def __len__(self):
        return len(self._intensities)

    def _get_intensity(self, transition, absorption, primary,
                       characteristic_fluorescence, bremsstrahlung_fluorescence):
        def _create_photon_keys2(transition):
            return _create_photon_keys(self._intensities, transition,
                                       absorption, primary,
                                       characteristic_fluorescence,
                                       bremsstrahlung_fluorescence)

        if isinstance(transition, str):
            transition = from_string(transition)

        # Collect photon keys
        list_keys = []
        if isinstance(transition, transitionset): # transitionset
            keys = _create_photon_keys2(transition)
            for key in keys:
                if key in self._intensities:
                    list_keys.append(key)
            else:
                for t in transition:
                    keys = _create_photon_keys2(t)
                    list_keys.extend(keys)
        else: # single transition
            keys = _create_photon_keys2(transition)
            list_keys.extend(keys)

        # Retrieve intensity (and its uncertainty)
        total_val = 0.0
        total_unc = 0.0
        for key in list_keys:
            intensity = self._intensities.get(key)
            if intensity is None:
                continue
            total_val += intensity[0][0]
            total_unc += intensity[0][1] ** 2

        total_unc = sqrt(total_unc)

        return total_val, total_unc

    def has_intensity(self, transition):
        """
        Returns whether the result contains an intensity for the specified
        transition.

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        """
        if isinstance(transition, str):
            transition = from_string(transition)

        for key in self._intensities.keys():
            if key.transition == transition:
                return True

        return False

    def intensity(self, transition, absorption=True, fluorescence=True):
        """
        Returns the intensity (and its uncertainty) in counts / (sr.electron).

        These examples will all returned the same values::

            >>> result.intensity(Transition(13, 4, 1))
            >>> result.intensity('Al Ka1')

        or

            >>> result.intensity(K_family(13))
            >>> result.intensity('Al K')

        Note that in the case of a set of transitions (e.g. family, shell),
        the intensity of each transition in the set is added.
        For instance, the following lines will yield the same result::

            >>> result.intensity('Al Ka1')[0] + result.intensity('Al Ka2')[0]
            >>> result.intensity('Al Ka')[0]

        Note that the ``[0]`` is to return the intensity part of the
        intensity/uncertainty tuple.

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.
        :arg fluorescence: whether to return the intensity with fluorescence.
            If ``True``, intensity with fluorescence is returned, if ``false``
            intensity without fluorescence.

        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        return self._get_intensity(transition, absorption, True,
                                   fluorescence, fluorescence)

    def characteristic_fluorescence(self, transition, absorption=True):
        """
        Returns the intensity (and its uncertainty) of the characteristic photons
        produced by fluorescence of primary photons in counts / (sr.electron).

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.

        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        return self._get_intensity(transition, absorption, False, True, False)

    def bremsstrahlung_fluorescence(self, transition, absorption=True):
        """
        Returns the intensity (and its uncertainty) of the Bremsstrahlung photons
        produced by fluorescence of primary photons in counts / (sr.electron).

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.

        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        return self._get_intensity(transition, absorption, False, False, True)

    def fluorescence(self, transition, absorption=True):
        """
        Returns the intensity (and its uncertainty) of the fluorescence
        contribution to the total intensity in counts / (sr.electron).

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg fluorescence: whether to return the intensity with fluorescence.
            If ``True``, intensity with fluorescence is returned, if ``false``
            intensity without fluorescence.

        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        return self._get_intensity(transition, absorption, False, True, True)

    def absorption(self, transition, fluorescence=True):
        """
        Returns the intensity (and its uncertainty) of the absorption
        contribution to the total intensity in counts / (sr.electron).

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.

        :return: intensity and its uncertainty
        :raise: :class:`ValueError` if there is no intensity for the specified
            transition
        """
        v1, e1 = self.intensity(transition, absorption=False, fluorescence=fluorescence)
        v2, e2 = self.intensity(transition, absorption=True, fluorescence=fluorescence)

        return v2 - v1, np.sqrt(e1 ** 2 + e2 ** 2)

    def iter_transitions(self, absorption=True, fluorescence=True):
        """
        Returns an iterator returning a tuple of the transition and intensity.

        :arg absorption: whether to return the intensity with absorption.
            If ``True``, emitted intensity is returned, if ``false`` generated
            intensity.
        :arg fluorescence: whether to return the intensity with fluorescence.
            If ``True``, intensity with fluorescence is returned, if ``false``
            intensity without fluorescence.
        """
        transitions = set()
        for key in self._intensities:
            transitions.add(key.transition)

        for transition in transitions:
            yield transition, self.intensity(transition, absorption, fluorescence)

class PhotonSpectrumResult(_Result):

    def __init__(self, total, background):
        """
        Stores results from a photon spectrum.

        All intensities are given in counts / (sr.eV.electron).
        In other words, the number of counts is normalized by the solid angle
        of the detector collecting the spectrum, the width of the energy
        channel and the number of simulated electrons.

        :arg total: numpy array containing 2 or 3 columns. The first column
            must be the mid-energy of each bin in eV, the second, the total intensity
            in counts/(sr.eV.electron) and the third (optional), the
            uncertainty on the total intensity.

        :arg background: numpy array containing 2 or 3 columns. The first column
            must be the mid-energy of each bin, the second, the background
            intensity in counts/(sr.eV.electron) and the third (optional), the
            uncertainty on the background intensity.

        .. note::

           The first column of the total and background arrays must be equal.
        """
        def _check(data):
            if data.shape[1] < 2:
                raise ValueError('The data must contains at least two columns')
            if data.shape[1] == 2:
                data = np.append(data, np.zeros((data.shape[0], 1)), 1)

            return data

        if not np.allclose(total[:, 0], background[:, 0]):
            raise ValueError('Energies are different for the total and background array')

        _Result.__init__(self)

        self._total = _check(total)
        self._background = _check(background)

    @property
    def energy_channel_width_eV(self):
        """
        Width of each energy channel in eV.
        """
        return self._total[1, 0] - self._total[0, 0]

    @property
    def energy_offset_eV(self):
        """
        Energy offset of the spectrum in eV.
        """
        return self._total[0, 0]

    def get_total(self):
        """
        Returns a numpy array where the first column is the mid-energy of each
        bin in eV, the second, the total intensity in counts/(sr.eV.electron)
        and the third (optional), the uncertainty on the total intensity.
        """
        return np.copy(self._total)

    def get_background(self):
        """
        Returns a numpy array where the first column is the mid-energy of each
        bin in eV, the second, the background intensity in counts/(sr.eV.electron)
        and the third (optional), the uncertainty on the background intensity.
        """
        return np.copy(self._background)

    def _get_intensity(self, energy_eV, data):
        """
        Returns the intensity and its uncertainty for the specified
        energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the
        spectrum.

        :arg energy_eV: energy of interest (in eV).
        :arg values: intensity values
        :arg uncs: uncertainty values
        """
        if energy_eV >= data[-1, 0] + self.energy_channel_width_eV:
            return 0.0, 0.0 # Above last channel

        index = bisect.bisect_right(data[:, 0], energy_eV)
        if not index:
            return 0.0, 0.0 # Below first channel

        return data[index - 1, 1:3]

    def total_intensity(self, energy_eV):
        """
        Returns the total intensity (in counts / (sr.eV.electron) and its
        uncertainty for the specified energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the
        spectrum.

        :arg energy_eV: energy of interest (in eV).
        """
        return self._get_intensity(energy_eV, self._total)

    def background_intensity(self, energy_eV):
        """
        Returns the background intensity (in counts / (sr.eV.electron) and its
        uncertainty for the specified energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the
        spectrum.

        :arg energy_eV: energy of interest (in eV).
        """
        return self._get_intensity(energy_eV, self._background)

class _PhotonDistributionResult(_Result):

    def __init__(self, distributions=None):
        """
        Creates a new result to store photon distributions.

        :arg distributions: :class:`dict` containing the distributions.
            The keys should be :class:`.PhotonKey` and the values a numpy array
            containing two or three columns:

              * abscissa values
              * intensities
              * (optional) uncertainties on the intensities
        """
        _Result.__init__(self)

        if distributions is None:
            distributions = {}

        self._distributions = {}
        for key, distribution in distributions.items():
            if distribution.shape[1] < 2:
                raise ValueError('The data must contains at least two columns')
            if distribution.shape[1] == 2:
                distribution = np.append(distribution, np.zeros((distribution.shape[0], 1)), 1)

            self._distributions[key] = distribution

    def __len__(self):
        return len(self._distributions)

    def exists(self, transition, absorption=True, fluorescence=True):
        """
        Returns whether the result contains a photon distribution for
        the specified transition.

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.get`)
        :arg absorption: distribution with absorption. If ``True``, emitted
            distribution is returned, if ``False`` generated distribution.
        :arg fluorescence: distribution with fluorescence. If ``True``,
            distribution with fluorescence is returned, if ``False``
            distribution without fluorescence.
        """
        if isinstance(transition, str):
            transition = from_string(transition)

        keys = _create_photon_keys(self._distributions, transition,
                                   absorption, True, fluorescence, fluorescence)
        return len(keys) == 1

    def _get(self, transition, absorption, primary,
             characteristic_fluorescence, bremsstrahlung_fluorescence):
        if isinstance(transition, str):
            transition = from_string(transition)

        keys = _create_photon_keys(self._distributions, transition,
                                   absorption, primary,
                                   characteristic_fluorescence,
                                   bremsstrahlung_fluorescence)
        if len(keys) != 1:
            raise ValueError('Distribution not found')

        return np.copy(self._distributions[keys[0]])

    def get(self, transition, absorption=True, fluorescence=True):
        """
        Returns the photon distribution for the specified transition.
        A Numpy array is returned where the columns are:

            * abscissa values
            * intensities
            * uncertainties on the intensities

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.

        :raise: :class:`ValueError` if there is no distribution for the
            specified transition.
        """
        return self._get(transition, absorption, True, fluorescence, fluorescence)

    def integral(self, transition, absorption=True, fluorescence=True):
        """
        Returns the integral over the photon distribution for the
        specified transition.

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.

        :rtype: :class:`float`
        """
        distribution = self.get(transition, absorption, fluorescence)
        rzs = distribution[:, 0]
        vals = distribution[:, 1]
        width = abs(rzs[1] - rzs[0])
        return sum(vals) * width

    def iter_transitions(self, absorption=True, fluorescence=True):
        """
        Returns an iterator returning a tuple of the:

          * transition
          * abscissa values
          * intensities
          * uncertainties on the intensities

        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.
        """
        transitions = set()
        for key in self._distributions:
            transitions.add(key.transition)

        for transition in transitions:
            if not self.exists(transition, absorption, fluorescence):
                continue

            distribution = self.get(transition, absorption, fluorescence)
            yield transition, distribution

class PhotonDepthResult(_PhotonDistributionResult):

    def exists(self, transition, absorption=True, fluorescence=True):
        """
        Returns whether the result contains a photon depth distribution for
        the specified transition.

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.get`)
        :arg absorption: distribution with absorption. If ``True``, emitted
            distribution is returned, if ``False`` generated distribution.
        :arg fluorescence: distribution with fluorescence. If ``True``,
            distribution with fluorescence is returned, if ``False``
            distribution without fluorescence.
        """
        return _PhotonDistributionResult.exists(self, transition, absorption, fluorescence)

    def get(self, transition, absorption=True, fluorescence=True):
        """
        Returns the photon depth distribution for the specified transition.
        A Numpy array is returned where the columns are:

            * z values (in meters)
            * intensities
            * uncertainties on the intensities

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.

        :raise: :class:`ValueError` if there is no distribution for the
            specified transition.

        Here are examples that will all returned the same values::

            >>> pz = result.get(Transition(13, 4, 1))
            >>> zs = pz[:,0]; vals = pz[:,1]
            >>> pz = result.get('Al Ka1')

        or

            >>> pz = result.get(K_family(13))
            >>> pz = result.get('Al K')
        """
        return _PhotonDistributionResult.get(self, transition, absorption, fluorescence)

    def integral(self, transition, absorption=True, fluorescence=True):
        """
        Returns the integral over the photon depth distribution for the
        specified transition (in meters).

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.

        :rtype: :class:`float`
        """
        return _PhotonDistributionResult.integral(self, transition, absorption, fluorescence)

    def fchi(self, transition, fluorescence=True):
        """
        Returns the ratio between the emitted over the generated photon depth
        distribution for the specified transition.

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.

        :rtype: :class:`float`
        """
        Fchi = self.integral(transition, True, fluorescence)
        F0chi = self.integral(transition, False, fluorescence)
        return Fchi / F0chi

    def iter_transitions(self, absorption=True, fluorescence=True):
        """
        Returns an iterator returning a tuple of the:

          * transition
          * depths (in meters)
          * intensities
          * uncertainties on the intensities

        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.
        """
        return _PhotonDistributionResult.iter_transitions(self, absorption, fluorescence)

class PhotonRadialResult(_PhotonDistributionResult):

    def exists(self, transition, absorption=True, fluorescence=True):
        """
        Returns whether the result contains a photon radial distribution for
        the specified transition.

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.get`)
        :arg absorption: distribution with absorption. If ``True``, emitted
            distribution is returned, if ``False`` generated distribution.
        :arg fluorescence: distribution with fluorescence. If ``True``,
            distribution with fluorescence is returned, if ``False``
            distribution without fluorescence.
        """
        return _PhotonDistributionResult.exists(self, transition, absorption, fluorescence)

    def get(self, transition, absorption=True, fluorescence=True):
        """
        Returns the photon depth distribution for the specified transition.
        A Numpy array is returned where the columns are:

            * radius values (in meters)
            * intensities (normalized by area)
            * uncertainties on the intensities

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.

        :raise: :class:`ValueError` if there is no distribution for the
            specified transition.

        Here are examples that will all returned the same values::

            >>> pz = result.get(Transition(13, 4, 1))
            >>> zs = pz[:,0]; vals = pz[:,1]
            >>> pz = result.get('Al Ka1')

        or

            >>> pz = result.get(K_family(13))
            >>> pz = result.get('Al K')
        """
        return _PhotonDistributionResult.get(self, transition, absorption, fluorescence)

    def integral(self, transition, absorption=True, fluorescence=True):
        """
        Returns the integral over the photon radial distribution for the
        specified transition (in meters).

        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.

        :rtype: :class:`float`
        """
        return _PhotonDistributionResult.integral(self, transition, absorption, fluorescence)

    def iter_transitions(self, absorption=True, fluorescence=True):
        """
        Returns an iterator returning a tuple of the:

          * transition
          * radial (in meters)
          * intensities (normalized by area)
          * uncertainties on the intensities

        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted photon depth distribution is returned,
            if ``False`` generated photon depth distribution.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, photon depth distribution with fluorescence is returned,
            if ``False`` photon depth distribution without fluorescence.
        """
        return _PhotonDistributionResult.iter_transitions(self, absorption, fluorescence)

class TimeResult(_Result):

    def __init__(self, simulation_time_s=0.0, simulation_speed_s=(0.0, 0.0)):
        """
        Creates a new result to store simulation time and speed.

        :arg simulation_time_s: total time of the simulation (in seconds)
        :arg simulation_speed_s: time to simulation one electron (in seconds) and
            its uncertainty
        """
        _Result.__init__(self)

        self._simulation_time_s = simulation_time_s

        if len(simulation_speed_s) != 2:
            raise ValueError("Simulation speed must be a tuple (value, uncertainty)")
        self._simulation_speed_s = simulation_speed_s

    @property
    def simulation_time_s(self):
        return self._simulation_time_s

    @property
    def simulation_speed_s(self):
        return self._simulation_speed_s

class ShowersStatisticsResult(_Result):

    def __init__(self, showers=0):
        """
        Creates a new result to store statistics about the showers.

        :arg showers: number of simulated particles
        """
        _Result.__init__(self)

        self._showers = int(showers)

    @property
    def showers(self):
        return self._showers

class ElectronFractionResult(_Result):

    def __init__(self, absorbed=(0.0, 0.0),
                        backscattered=(0.0, 0.0),
                        transmitted=(0.0, 0.0)):
        _Result.__init__(self)

        if len(absorbed) != 2:
            raise ValueError("Absorbed fraction must be a tuple (value, uncertainty)")
        self._absorbed = absorbed

        if len(backscattered) != 2:
            raise ValueError("Backscattered fraction must be a tuple (value, uncertainty)")
        self._backscattered = backscattered

        if len(transmitted) != 2:
            raise ValueError("Transmitted fraction must be a tuple (value, uncertainty)")
        self._transmitted = transmitted

    @property
    def absorbed(self):
        return self._absorbed

    @property
    def backscattered(self):
        return self._backscattered

    @property
    def transmitted(self):
        return self._transmitted

EXIT_STATE_TRANSMITTED = 1
EXIT_STATE_BACKSCATTERED = 2
EXIT_STATE_ABSORBED = 3

EXIT_STATES = frozenset([EXIT_STATE_BACKSCATTERED, EXIT_STATE_TRANSMITTED,
                         EXIT_STATE_ABSORBED])

class Trajectory(object):
    def __init__(self, primary, particle, collision, exit_state, interactions):
        """
        Container for one trajectory.

        :arg primary: whether the trajectory corresponds to a primary particle
        :type primary: :class:`bool`

        :arg particle: type of particle
            (:const:`ELECTRON`, :const:`Photon` or :const:`POSITRON`)
        :type particle: :class:`_Particle`

        :arg collision: type of collision that created this trajectory
        :type collision: :class:`_Collision`

        :arg exit_state: exit state flag (backscattered, transmitted or absorbed)

        :arg interactions: two-dimensional array where each row corresponds
            to an interaction of the particle. The columns are defined as
            follows:

                #. x position (in m)
                #. y position (in m)
                #. z position (in m)
                #. energy at position (in eV)
                #. type of collision
                #. region

            The array can contain more columns.
        :type: :class:`ndarray`
        """
        self._primary = primary
        self._particle = particle
        self._collision = collision
        self._exit_state = exit_state
        self._interactions = interactions

    def __repr__(self):
        primary = {True: 'primary', False: 'secondary'}[self._primary]
        particle = str(self._particle).lower()
        collision = str(self._collision)
        exit_state = {EXIT_STATE_ABSORBED: 'absorbed',
                      EXIT_STATE_BACKSCATTERED: 'backscattered',
                      EXIT_STATE_TRANSMITTED: 'transmitted'}.get(self.exit_state)
        interactions_count = len(self.interactions)

        if self.is_primary():
            return '<Trajectory(%s %s %s with %i interactions)>' % \
                (primary, exit_state, particle, interactions_count)
        else:
            return '<Trajectory(%s %s %s from %s with %i interactions)>' % \
                (primary, exit_state, particle, collision, interactions_count)

    @property
    def particle(self):
        """
        Returns the type of particle.
        """
        return self._particle

    @property
    def collision(self):
        """
        Returns the type of collision that created this trajectory.
        """
        return self._collision

    @property
    def exit_state(self):
        """
        Returns the exit state flag:

            * :const:`EXIT_STATE_BACKSCATTERED`
            * :const:`EXIT_STATE_TRANSMITTED`
            * :const:`EXIT_STATE_ABSORBED`
        """
        return self._exit_state

    @property
    def interactions(self):
        """
        Returns two-dimensional array where each row corresponds to an
        interaction of the particle.
        The first three columns must be the x, y and z position (in m) of the
        interaction, the fourth column, the energy at the position (in eV) and
        the fifth, the type of collision.
        The array can contain more columns.
        """
        return self._interactions

    def is_primary(self):
        """
        Returns whether this trajectory is from a primary particle.
        """
        return self._primary

    def is_secondary(self):
        """
        Returns whether this trajectory is from a secondary particle.
        """
        return not self._primary

class TrajectoryResult(_Result, Iterable, Sized):

    def __init__(self, trajectories=[]):
        self._trajectories = trajectories

    def __len__(self):
        return len(self._trajectories)

    def __iter__(self):
        return iter(self._trajectories)

    def filter(self, is_primary=[True, False], particles=PARTICLES,
               collisions=COLLISIONS, exit_states=EXIT_STATES):
        """
        Filters the trajectories based on the specified criteria.
        Each criterion can a single value or a list of accepted values.
        Returns an iterator.

        :arg is_primary: whether to include primary particles. Possible values:

            * ``True``: only primary particles
            * ``False``: only secondary particles
            * ``[True, False]``: both primary and secondary particles

        :type is_primary: :class:`bool` or :class:`list`

        :arg particles: which particle(s) to include
        :type particles: :class:`_Particle` or :class:`list`

        :arg collisions: which collision(s) from which a trajectory initiated to
            include.
        :type collisions: :class:`_Collision` or :class:`list`

        :arg exit_states: which exit state(s) of a trajectory to include
        :type exit_states: :class:`int` or :class:`list`
        """
        if not hasattr(is_primary, '__contains__'): is_primary = [is_primary]
        if not hasattr(particles, '__contains__'): particles = [particles]
        if not hasattr(collisions, '__contains__'): collisions = [collisions]
        if not hasattr(exit_states, '__contains__'): exit_states = [exit_states]

        for trajectory in self:
            if trajectory._primary not in is_primary: continue
            if trajectory.particle not in particles: continue
            if trajectory.collision not in collisions: continue
            if trajectory.exit_state not in exit_states: continue

            yield trajectory

class _ChannelsResult(_Result):

    def __init__(self, data):
        """
        Creates a new result to store a distribution.

        :arg data: numpy array containing 2 or 3 columns. The first column
            must be the mid-value of each bin, the second, the probability
            density and the third (optional), the uncertainty (3 sigma) on
            the probability density.
        """
        _Result.__init__(self)

        if data.shape[1] < 2:
            raise ValueError('The data must contains at least two columns')
        if data.shape[1] == 2:
            data = np.append(data, np.zeros((data.shape[0], 1)), 1)

        self._data = data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def get_data(self):
        return np.copy(self._data)

class BackscatteredElectronEnergyResult(_ChannelsResult):
    """
    Energy distribution of backscattered electrons.

    Data columns:

        1. Mid-energy of each bin (eV)
        2. probability density (counts/(eV.electron))
        3. uncertainty of the probability density (counts/(eV.electron))
    """
    pass

class TransmittedElectronEnergyResult(_ChannelsResult):
    """
    Energy distribution of transmitted electrons.

    Data columns:

        1. Mid-energy of each bin (eV)
        2. probability density (counts/(eV.electron))
        3. uncertainty of the probability density (counts/(eV.electron))
    """
    pass

class BackscatteredElectronPolarAngularResult(_ChannelsResult):
    """
    Angular distribution of backscattered electrons.

    Data columns:

        1. Mid-angle of each bin (rad)
        2. probability density (counts/(eV.electron))
        3. uncertainty of the probability density (counts/(eV.electron))
    """
    pass

class BackscatteredElectronRadialResult(_ChannelsResult):
    """
    Radial distribution of backscattered electrons.

    Data columns:

        1. Mid-distance of each bin (meters)
        2. probability density, area normalized (counts/(eV.electron.m2))
        3. uncertainty of the probability density (counts/(eV.electron.m2))
    """
    pass


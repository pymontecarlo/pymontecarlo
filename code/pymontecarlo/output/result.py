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
import csv
import os
import bisect
import tempfile
import shutil
import math
from math import sqrt
from collections import Iterable, Sized
from StringIO import StringIO
from xml.etree.ElementTree import Element, tostring, fromstring

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.util.transition import from_string
from pymontecarlo.output.manager import ResultManager

# Globals and constants variables.
from pymontecarlo.input.particle import PARTICLES
from pymontecarlo.input.collision import COLLISIONS

GENERATED = "g"
EMITTED = "e"
NOFLUORESCENCE = "nf"
CHARACTERISTIC = "cf"
BREMSSTRAHLUNG = "bf"
TOTAL = "t"

class _Result(object):
    """
    Base class of all results. 
    A result is a read-only class where results of a detector are stored.
    
    Derived classes must implement :meth:`__loadzip__` and :meth:`__savezip__`
    which respectively load and save the result to a ZIP file.
    
    Each result class must be register in the ResultManager.
    """

    @classmethod
    def __loadzip__(cls, zipfile, key):
        return cls()

    def __savezip__(self, zipfile, key):
        pass

def create_intensity_dict(transition,
                          gcf=(0.0, 0.0), gbf=(0.0, 0.0), gnf=(0.0, 0.0), gt=(0.0, 0.0),
                          ecf=(0.0, 0.0), ebf=(0.0, 0.0), enf=(0.0, 0.0), et=(0.0, 0.0)):
    return {transition: {
                GENERATED: {
                    CHARACTERISTIC: gcf,
                    BREMSSTRAHLUNG: gbf,
                    NOFLUORESCENCE: gnf,
                    TOTAL: gt},
                EMITTED: {
                    CHARACTERISTIC: ecf,
                    BREMSSTRAHLUNG: ebf,
                    NOFLUORESCENCE: enf,
                    TOTAL: et}
                         }
            }

class PhotonIntensityResult(_Result):
    _COLUMNS = ['transition', 'energy (eV)',
                'generated characteristic', 'generated characteristic unc',
                'generated bremsstrahlung', 'generated bremsstrahlung unc',
                'generated no fluorescence', 'generated no fluorescence unc',
                'generated total', 'generated total unc',
                'emitted characteristic', 'emitted characteristic unc',
                'emitted bremsstrahlung', 'emitted bremsstrahlung unc',
                'emitted no fluorescence', 'emitted no fluorescence unc',
                'emitted total', 'emitted total unc']

    def __init__(self, intensities={}):
        """
        Creates a new result to store photon intensities.
        
        :arg intensities: :class:`dict` containing the intensities.
            One should use :func:`.create_intensity_dict` to create the dictionary
        """
        _Result.__init__(self)

        # Check structure
        def _check1(transition, data, key1, name1):
            if key1 not in data:
                raise ValueError, "Transition %s is missing %s intensities" % \
                        (transition, name1)

        def _check2(transition, data, key1, name1, key2, name2):
            if key2 not in data[key1]:
                raise ValueError, "Transition %s is missing %s %s intensities" % \
                        (transition, name1, name2)

            if len(data[key1][key2]) != 2:
                raise ValueError, 'Intensity for %s %s %s must be a tuple (value, uncertainty)' % \
                    (transition, name1, name2)

        for transition, data in intensities.iteritems():
            _check1(transition, data, GENERATED, 'generated')
            _check1(transition, data, EMITTED, 'emitted')

            _check2(transition, data, GENERATED, 'generated', CHARACTERISTIC, 'characteristic')
            _check2(transition, data, GENERATED, 'generated', BREMSSTRAHLUNG, 'bremsstrahlung')
            _check2(transition, data, GENERATED, 'generated', NOFLUORESCENCE, 'no fluorescence')
            _check2(transition, data, GENERATED, 'generated', TOTAL, 'total')

            _check2(transition, data, EMITTED, 'emitted', CHARACTERISTIC, 'characteristic')
            _check2(transition, data, EMITTED, 'emitted', BREMSSTRAHLUNG, 'bremsstrahlung')
            _check2(transition, data, EMITTED, 'emitted', NOFLUORESCENCE, 'no fluorescence')
            _check2(transition, data, EMITTED, 'emitted', TOTAL, 'total')

        self._intensities = intensities

    @classmethod
    def __loadzip__(cls, zipfile, key):
        reader = csv.reader(zipfile.open(key + '.csv', 'r'))

        header = reader.next()
        if header != cls._COLUMNS:
            raise IOError, 'Header of "%s.csv" is invalid' % key

        intensities = {}
        for row in reader:
            transition = from_string(row[0])
            # skip row[1] (energy)

            gcf = float(row[2]), float(row[3])
            gbf = float(row[4]), float(row[5])
            gnf = float(row[6]), float(row[7])
            gt = float(row[8]), float(row[9])

            ecf = float(row[10]), float(row[11])
            ebf = float(row[12]), float(row[13])
            enf = float(row[14]), float(row[15])
            et = float(row[16]), float(row[17])

            intensities.update(create_intensity_dict(transition,
                                                     gcf, gbf, gnf, gt,
                                                     ecf, ebf, enf, et))

        return cls(intensities)

    def __savezip__(self, zipfile, key):
        fp = StringIO()
        writer = csv.writer(fp)

        writer.writerow(self._COLUMNS)

        for transition, intensities in self._intensities.iteritems():
            row = []
            row.append(str(transition))
            if hasattr(transition, 'energy_eV'):
                row.append(transition.energy_eV)
            else:
                row.append(0.0)

            row.extend(intensities[GENERATED][CHARACTERISTIC])
            row.extend(intensities[GENERATED][BREMSSTRAHLUNG])
            row.extend(intensities[GENERATED][NOFLUORESCENCE])
            row.extend(intensities[GENERATED][TOTAL])

            row.extend(intensities[EMITTED][CHARACTERISTIC])
            row.extend(intensities[EMITTED][BREMSSTRAHLUNG])
            row.extend(intensities[EMITTED][NOFLUORESCENCE])
            row.extend(intensities[EMITTED][TOTAL])

            writer.writerow(row)

        zipfile.writestr(key + '.csv', fp.getvalue())

    def __contains__(self, transition):
        return self.has_intensity(transition)

    def _get_intensity(self, key, transition, absorption=True):
        if isinstance(transition, basestring):
            transition = from_string(transition)

        # Get intensity data
        data = []
        if isinstance(transition, Iterable): # transitionset
            if transition in self._intensities:
                data.append(self._intensities[transition])
            else:
                for t in transition:
                    if t in self._intensities: # Add only known transitions
                        data.append(self._intensities[t])

            if not data:
                raise ValueError, "No intensity for transition(s): %s" % transition
        else: # single transition
            try:
                data.append(self._intensities[transition])
            except KeyError:
                raise ValueError, "No intensity for transition(s): %s" % transition

        # Retrieve intensity (and its uncertainty)
        absorption_key = EMITTED if absorption else GENERATED
        total_val = 0.0; total_unc = 0.0
        for datum in data:
            val, unc = datum[absorption_key][key]
            total_val += val
            try:
                total_unc += (unc / val) ** 2
            except ZeroDivisionError: # if val == 0.0
                pass

        total_unc = sqrt(total_unc) * total_val

        return total_val, total_unc

    def has_intensity(self, transition):
        """
        Returns whether the result contains an intensity for the specified 
        transition.
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.intensity`)
        """
        if isinstance(transition, basestring):
            transition = from_string(transition)

        # Get intensity data
        data = []
        if isinstance(transition, Iterable): # transitionset
            if transition in self._intensities:
                data.append(self._intensities[transition])
            else:
                for t in transition:
                    if t in self._intensities: # Add only known transitions
                        data.append(self._intensities[t])

            if not data:
                return False
        else: # single transition
            if not self._intensities.has_key(transition):
                return False

        return True

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
        key = TOTAL if fluorescence else NOFLUORESCENCE
        return self._get_intensity(key, transition, absorption)

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
        return self._get_intensity(CHARACTERISTIC, transition, absorption)

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
        return self._get_intensity(BREMSSTRAHLUNG, transition, absorption)

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
        # Note: TOTAL - FLUORESCENCE should be equal to CHARACTERISTIC + BREMSS
        v1, e1 = self._get_intensity(NOFLUORESCENCE, transition, absorption)
        v2, e2 = self._get_intensity(TOTAL, transition, absorption)

        return v2 - v1, e1 + e2

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

        return v2 - v1, e1 + e2

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
        for transition in self._intensities:
            yield transition, self.intensity(transition, absorption, fluorescence)

ResultManager.register('PhotonIntensityResult', PhotonIntensityResult)

class PhotonSpectrumResult(_Result):
    _COLUMNS = ['energy (eV)',
                'total', 'total unc',
                'background', 'background unc']

    def __init__(self, energy_offset_eV, energy_channel_width_eV,
                        total, total_unc=None,
                        background=None, background_unc=None):
        """
        Stores results from a photon spectrum.
        
        All intensities are given in counts / (sr.eV.electron). 
        In other words, the number of counts is normalized by the solid angle 
        of the detector collecting the spectrum, the width of the energy 
        channel and the number of simulated electrons.
        
        :arg energy_offset_eV: energy (in eV) of the first channel.
        :type energy_offset_eV: :class:`float`
        
        :arg energy_channel_width_eV: width of each energy channel (in eV)
        :type energy_channel_width_eV: :class:`float`
        
        :arg total: total intensities of each channel in counts / (sr.eV.electron). 
        :type intensities: :class:`list` of :class:`float`
        
        :arg total_unc: uncertainties on the total intensity of each channel in 
            counts / (sr.eV.electron). 
            The uncertainties should correspond to 3 sigma statistical 
            uncertainty.
            If ``None``, the uncertainty of all channels is set to 0.0.
        :type intensities_unc: :class:`list` of :class:`float`
        
        :arg background: background intensities of each channel in 
            counts / (sr.eV.electron).
            The background intensity is the total intensity without the 
            intensity from the characteristic photons.
            If ``None``, the background intensities are set to 0.0.
        :type backgrounds: :class:`list` of :class:`float`
        
        :arg background_unc: uncertainties on the background intensity of each 
            channel in counts / (sr.eV.electron). 
            The uncertainties should correspond to 3 sigma statistical 
            uncertainty.
            If ``None``, the uncertainty of all channels is set to 0.0.
        :type backgrounds_unc: :class:`list` of :class:`float`
        """
        _Result.__init__(self)

        if total_unc is None: total_unc = [0.0] * len(total)
        if background is None: background = [0.0] * len(total)
        if background_unc is None: background_unc = [0.0] * len(total)

        if len(total) != len(total_unc):
            raise ValueError, \
                'The number of total intensities (%i) must match the number of uncertainties (%i)' % \
                    (len(total), len(total_unc))
        if len(background) != len(total):
            raise ValueError, \
                'The number of background intensities (%i) must match the number of total intensities (%i)' % \
                    (len(background), len(total))
        if len(background) != len(background_unc):
            raise ValueError, \
                'The number of background intensities (%i) must match the number of uncertainties (%i)' % \
                    (len(background), len(background_unc))

        self._energies_eV = [i * float(energy_channel_width_eV) + energy_offset_eV \
                             for i in range(len(total))]
        self._total = total
        self._total_unc = total_unc
        self._background = background
        self._background_unc = background_unc

    @classmethod
    def __loadzip__(cls, zipfile, key):
        reader = csv.reader(zipfile.open(key + '.csv', 'r'))

        header = reader.next()
        if header != cls._COLUMNS:
            raise IOError, 'Header of "%s.csv" is invalid' % key

        energies_eV = []
        total = []
        total_unc = []
        background = []
        background_unc = []
        for row in reader:
            energies_eV.append(float(row[0]))
            total.append(float(row[1]))
            total_unc.append(float(row[2]))
            background.append(float(row[3]))
            background_unc.append(float(row[4]))

        energy_offset_eV = energies_eV[0]
        energy_channel_width_eV = energies_eV[1] - energies_eV[0]

        return cls(energy_offset_eV, energy_channel_width_eV,
                   total, total_unc, background, background_unc)

    def __savezip__(self, zipfile, key):
        fp = StringIO()
        writer = csv.writer(fp)

        writer.writerow(self._COLUMNS)

        for row in zip(self._energies_eV, self._total, self._total_unc,
                       self._background, self._background_unc):
            writer.writerow(row)

        zipfile.writestr(key + '.csv', fp.getvalue())

    @property
    def energy_channel_width_eV(self):
        """
        Width of each energy channel in eV.
        """
        return self._energies_eV[1] - self._energies_eV[0]

    @property
    def energy_offset_eV(self):
        """
        Energy offset of the spectrum in eV. 
        """
        return self._energies_eV[0]

    def get_total(self):
        """
        Returns the energies (in eV), the total intensities (in 
        counts / (sr.eV.electron) and the 3 sigma uncertainty on the total 
        intensities.
        """
        # Note: list(...) is used to return a copy of the energies and intensities
        return list(self._energies_eV), list(self._total), list(self._total_unc)

    def get_background(self):
        """
        Returns the energies (in eV), the background intensities (in 
        counts / (sr.eV.electron) and the 3 sigma uncertainty on the background 
        intensities.
        """
        # Note: list(...) is used to return a copy of the energies and intensities
        return list(self._energies_eV), list(self._background), list(self._background_unc)

    def _get_intensity(self, energy_eV, values, uncs):
        """
        Returns the intensity and its uncertainty for the specified 
        energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the 
        spectrum.
    
        :arg energy_eV: energy of interest (in eV).
        :arg values: intensity values
        :arg uncs: uncertainty values
        """
        if energy_eV >= self._energies_eV[-1] + self.energy_channel_width_eV:
            return 0.0, 0.0 # Above last channel

        index = bisect.bisect_right(self._energies_eV, energy_eV)
        if not index:
            return 0.0, 0.0 # Below first channel

        return values[index - 1], uncs[index - 1]

    def total_intensity(self, energy_eV):
        """
        Returns the total intensity (in counts / (sr.eV.electron) and its 
        uncertainty for the specified energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the 
        spectrum.
    
        :arg energy_eV: energy of interest (in eV).
        """
        return self._get_intensity(energy_eV, self._total, self._total_unc)

    def background_intensity(self, energy_eV):
        """
        Returns the background intensity (in counts / (sr.eV.electron) and its 
        uncertainty for the specified energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the 
        spectrum.
    
        :arg energy_eV: energy of interest (in eV).
        """
        return self._get_intensity(energy_eV, self._background, self._background_unc)

ResultManager.register('PhotonSpectrumResult', PhotonSpectrumResult)

def create_phirhoz_dict(transition, gnf=None, gt=None, enf=None, et=None):
    """
    Values of *gnf*, *gt*, *enf* and *et* must be a :class:`tuple` of three
    :class:`list` containing:
    
        * :math:`\\rho z` values (in kg/m2)
        * intensities
        * uncertainties on the intensities
    
    The values of :math:`\\rho z` must all be positive in ascending order and
    following a regular interval: :math:`|\\rho z_i - \\rho z_{i+1}| = k`
    """
    dist = {transition: {}}

    if gnf is not None:
        dist[transition].setdefault(GENERATED, {})[NOFLUORESCENCE] = gnf
    if gt is not None:
        dist[transition].setdefault(GENERATED, {})[TOTAL] = gt
    if enf is not None:
        dist[transition].setdefault(EMITTED, {})[NOFLUORESCENCE] = enf
    if et is not None:
        dist[transition].setdefault(EMITTED, {})[TOTAL] = et

    return dist

class PhiRhoZResult(_Result):
    _COLUMNS = ['depth (kg/m2)', 'intensity', 'unc']

    def __init__(self, distributions={}):
        """
        Creates a new result to store :math:`\\phi(\\rho z)` distributions.
        
        :arg distributions: :class:`dict` containing the distributions.
            One should use :func:`.create_phirhoz_dict` to create the dictionary
        """
        _Result.__init__(self)
        self._distributions = distributions

    @classmethod
    def __loadzip__(cls, zipfile, key):
        # Find all phi-rho-z files
        arcnames = [name for name in zipfile.namelist() if name.startswith(key)]

        # Read files
        data = {}
        for arcname in arcnames:
            parts = os.path.splitext(arcname)[0].split('+')
            transition = from_string(parts[-2].replace('_', ' '))
            suffix = parts[-1]

            reader = csv.reader(zipfile.open(arcname, 'r'))

            header = reader.next()
            if header != cls._COLUMNS:
                raise IOError, 'Header of "%s.csv" is invalid' % arcname

            zs = []
            values = []
            uncs = []
            for row in reader:
                zs.append(float(row[0]))
                values.append(float(row[1]))
                uncs.append(float(row[2]))

            data.setdefault(transition, {})[suffix] = zs, values, uncs

        # Construct distributions
        distributions = {}
        for transition, datum in data.iteritems():
            distributions.update(create_phirhoz_dict(transition, **datum))

        return cls(distributions)

    def __savezip__(self, zipfile, key):
        distributions = [('gnf', False, False), ('gt', False, True),
                         ('enf', True, False), ('et', True, True)]

        for suffix, absorption, fluorescence in distributions:
            for transition, zs, values, uncs in \
                    self.iter_transitions(absorption, fluorescence):
                fp = StringIO()
                writer = csv.writer(fp)

                writer.writerow(self._COLUMNS)

                for row in zip(zs, values, uncs):
                    writer.writerow(row)

                arcname = '+'.join([key, str(transition).replace(' ', '_'), suffix])
                zipfile.writestr(arcname + '.csv', fp.getvalue())

    def exists(self, transition, absorption=True, fluorescence=True):
        """
        Returns whether the result contains a :math:`\\phi(\\rho z)`
        distribution for the specified transition.
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples in :meth:`.get`)
        :arg absorption: distribution with absorption. If ``True``, emitted 
            distribution is returned, if ``False`` generated distribution.
        :arg fluorescence: distribution with fluorescence. If ``True``, 
            distribution with fluorescence is returned, if ``False`` 
            distribution without fluorescence.
        """
        if isinstance(transition, basestring):
            transition = from_string(transition)

        if transition not in self._distributions:
            return False

        absorption_key = EMITTED if absorption else GENERATED
        if absorption_key not in self._distributions[transition]:
            return False

        fluorescence_key = TOTAL if fluorescence else NOFLUORESCENCE
        if fluorescence_key not in self._distributions[transition][absorption_key]:
            return False

        return True

    def get(self, transition, absorption=True, fluorescence=True):
        """
        Returns the :math:`\\phi(\\rho z)` distribution for the specified 
        transition.
        Three :class:`list` are returned representing:
            
            * :math:`\\rho z` values (in kg/m2)
            * intensities
            * uncertainties on the intensities
            
        Each of these three lists have the same number of values.
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted :math:`\\phi(\\rho z)` is returned, 
            if ``False`` generated :math:`\\phi(\\rho z)`.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, :math:`\\phi(\\rho z)` with fluorescence is returned, 
            if ``False`` :math:`\\phi(\\rho z)` without fluorescence.
            
        :return: :math:`\\rho z` values (in kg/m2), intensities and
            uncertainties on the intensities
        :raise: :class:`ValueError` if there is no distribution for the 
            specified transition.
            
        Here are examples that will all returned the same values::
        
            >>> rzs, vals, uncs = result.get(Transition(13, 4, 1))
            >>> rzs, vals, uncs = result.get('Al Ka1')
        
        or
        
            >>> rzs, vals, uncs = result.get(K_family(13))
            >>> rzs, vals, uncs = result.get('Al K')
        """
        if isinstance(transition, basestring):
            transition = from_string(transition)

        # Check existence
        if not self.exists(transition, absorption, fluorescence):
            raise ValueError, "No distribution for transition(s): %s" % transition

        # Retrieve data
        absorption_key = EMITTED if absorption else GENERATED
        fluorescence_key = TOTAL if fluorescence else NOFLUORESCENCE

        zs, values, uncs = \
            self._distributions[transition][absorption_key][fluorescence_key]

        # Note: list(...) is used to return a copy
        return list(zs), list(values), list(uncs)

    def integral(self, transition, absorption=True, fluorescence=True):
        """
        Returns the integral over the phi-rho-z for the specified transition 
        in kg/m2.
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg absorption: whether to use the :math:`\\phi(\\rho z)` with 
            absorption. If ``True``, emitted :math:`\\phi(\\rho z)` is used, 
            if ``False`` generated :math:`\\phi(\\rho z)`.
        :arg fluorescence: whether to use math:`\\phi(\\rho z)` with 
            fluorescence. If ``True``, :math:`\\phi(\\rho z)` with fluorescence 
            is used, if ``False`` :math:`\\phi(\\rho z)` without fluorescence.
            
        :rtype: :class:`float`
        """
        rzs, vals, _uncs = self.get(transition, absorption, fluorescence)
        width = abs(rzs[1] - rzs[0])
        return sum(vals) * width

    def fchi(self, transition, fluorescence=True):
        """
        Returns the ratio between the emitted over the generated phi-rho-zs for 
        the specified transition.
        
        :arg transition: transition or set of transitions or name of the
            transition or transitions set (see examples)
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, :math:`\\phi(\\rho z)` with fluorescence is used, 
            if ``False`` :math:`\\phi(\\rho z)` without fluorescence.
            
        :rtype: :class:`float`
        """
        Fchi = self.integral(transition, True, fluorescence)
        F0chi = self.integral(transition, False, fluorescence)
        return Fchi / F0chi

    def iter_transitions(self, absorption=True, fluorescence=True):
        """
        Returns an iterator returning a tuple of the:

          * transition
          * depths (in kg/m2)
          * intensities
          * uncertainties on the intensities
        
        :arg absorption: whether to return the distribution with absorption.
            If ``True``, emitted intensity is returned, if ``False`` generated
            intensity.
        :arg fluorescence: whether to return the distribution with fluorescence.
            If ``True``, intensity with fluorescence is returned, if ``False``
            intensity without fluorescence.
        """
        for transition in self._distributions:
            if not self.exists(transition, absorption, fluorescence):
                continue

            zs, values, uncs = self.get(transition, absorption, fluorescence)
            yield transition, zs, values, uncs

ResultManager.register('PhiRhoZResult', PhiRhoZResult)

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
            raise ValueError, "Simulation speed must be a tuple (value, uncertainty)"
        self._simulation_speed_s = simulation_speed_s

    @classmethod
    def __loadzip__(cls, zipfile, key):
        element = fromstring(zipfile.open(key + '.xml', 'r').read())

        child = element.find('time')
        if child is not None:
            simulation_time = float(child.get('val', 0.0))
        else:
            simulation_time = 0.0

        child = element.find('speed')
        if child is not None:
            simulation_speed = \
                float(child.get('val', 0.0)), float(child.get('unc', 0.0))
        else:
            simulation_speed = (0.0, 0.0)

        return cls(simulation_time, simulation_speed)

    def __savezip__(self, zipfile, key):
        element = Element('result')

        attr = {'val': str(self.simulation_time_s)}
        child = Element('time', attr)
        element.append(child)

        attr = dict(zip(['val', 'unc'], map(str, self.simulation_speed_s)))
        child = Element('speed', attr)
        element.append(child)

        zipfile.writestr(key + '.xml', tostring(element))

    @property
    def simulation_time_s(self):
        return self._simulation_time_s

    @property
    def simulation_speed_s(self):
        return self._simulation_speed_s

ResultManager.register('TimeResult', TimeResult)

class ElectronFractionResult(_Result):

    def __init__(self, absorbed=(0.0, 0.0),
                        backscattered=(0.0, 0.0),
                        transmitted=(0.0, 0.0)):
        _Result.__init__(self)

        if len(absorbed) != 2:
            raise ValueError, "Absorbed fraction must be a tuple (value, uncertainty)"
        self._absorbed = absorbed

        if len(backscattered) != 2:
            raise ValueError, "Backscattered fraction must be a tuple (value, uncertainty)"
        self._backscattered = backscattered

        if len(transmitted) != 2:
            raise ValueError, "Transmitted fraction must be a tuple (value, uncertainty)"
        self._transmitted = transmitted

    @classmethod
    def __loadzip__(cls, zipfile, key):
        element = fromstring(zipfile.open(key + '.xml', 'r').read())

        child = element.find('absorbed')
        if child is not None:
            absorbed = \
                float(child.get('val', 0.0)), float(child.get('unc', 0.0))
        else:
            absorbed = (0.0, 0.0)

        child = element.find('backscattered')
        if child is not None:
            backscattered = \
                float(child.get('val', 0.0)), float(child.get('unc', 0.0))
        else:
            backscattered = (0.0, 0.0)

        child = element.find('transmitted')
        if child is not None:
            transmitted = \
                float(child.get('val', 0.0)), float(child.get('unc', 0.0))
        else:
            transmitted = (0.0, 0.0)

        return cls(absorbed, backscattered, transmitted)

    def __savezip__(self, zipfile, key):
        element = Element('result')

        attr = dict(zip(['val', 'unc'], map(str, self.absorbed)))
        child = Element('absorbed', attr)
        element.append(child)

        attr = dict(zip(['val', 'unc'], map(str, self.backscattered)))
        child = Element('backscattered', attr)
        element.append(child)

        attr = dict(zip(['val', 'unc'], map(str, self.transmitted)))
        child = Element('transmitted', attr)
        element.append(child)

        zipfile.writestr(key + '.xml', tostring(element))

    @property
    def absorbed(self):
        return self._absorbed

    @property
    def backscattered(self):
        return self._backscattered

    @property
    def transmitted(self):
        return self._transmitted

ResultManager.register('ElectronFractionResult', ElectronFractionResult)

EXIT_STATE_BACKSCATTERED = 1
EXIT_STATE_TRANSMITTED = 2
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
            to an interaction of the particle. The first three columns must
            be the x, y and z position (in m) of the interaction, the fourth
            column, the energy at the position (in eV) and the fifth, the type 
            of collision. The array can contain more columns.
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

    @classmethod
    def __loadzip__(cls, zipfile, key):
        tmpdir = tempfile.mkdtemp()
        filename = key + '.h5'
        zipfile.extract(filename, tmpdir)

        h5file = h5py.File(os.path.join(tmpdir, filename), 'r')

        return TrajectoryHDF5Result(h5file, tmpdir)

    def __savezip__(self, zipfile, key):
        # Create temporary folder
        tmpdir = tempfile.mkdtemp()
        filepath = os.path.join(tmpdir, key + '.h5')

        # Create HDF5 file
        h5file = h5py.File(filepath, 'w')
        h5group = h5file.create_group('trajectories')

        # Save trajectories
        width = int(math.floor(math.log10(len(self)))) + 1

        for index, trajectory in enumerate(self._trajectories):
            name = 'trajectory%s' % str(index).zfill(width)
            dataset = h5group.create_dataset(name, data=trajectory.interactions)

            dataset.attrs['primary'] = trajectory.is_primary()
            dataset.attrs['particle'] = str(trajectory.particle)
            dataset.attrs['collision'] = str(trajectory.collision)
            dataset.attrs['exit_state'] = trajectory.exit_state

        # Close HDF5, write file to zip, remove temporary folder
        h5file.close()
        zipfile.write(filepath, key + '.h5')
        shutil.rmtree(tmpdir, ignore_errors=True)

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

ResultManager.register('TrajectoryResult', TrajectoryResult)

class TrajectoryHDF5Result(TrajectoryResult):

    def __init__(self, h5file, tmpdir):
        self._h5file = h5file
        self._tmpdir = tmpdir

    def __del__(self):
        self._h5file.close()
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def __savezip__(self, zipfile, key):
        pass

    def __len__(self):
        return len(self._h5file['trajectories'])

    def __iter__(self):
        particles_ref = list(PARTICLES)
        particles_ref = dict(zip(map(str, particles_ref), particles_ref))

        collisions_ref = list(COLLISIONS)
        collisions_ref = dict(zip(map(str, collisions_ref), collisions_ref))

        for dataset in self._h5file['trajectories'].itervalues():
            primary = bool(dataset.attrs['primary'])
            particle = particles_ref.get(dataset.attrs['particle'])
            collision = collisions_ref.get(dataset.attrs['collision'])
            exit_state = int(dataset.attrs['exit_state'])
            interactions = dataset[:]

            yield Trajectory(primary, particle, collision, exit_state, interactions)

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

        particles_ref = list(PARTICLES)
        particles_ref = dict(zip(map(str, particles_ref), particles_ref))

        collisions_ref = list(COLLISIONS)
        collisions_ref = dict(zip(map(str, collisions_ref), collisions_ref))

        for dataset in self._h5file['trajectories'].itervalues():
            primary = bool(dataset.attrs['primary'])
            particle = particles_ref.get(dataset.attrs['particle'])
            collision = collisions_ref.get(dataset.attrs['collision'])
            exit_state = int(dataset.attrs['exit_state'])

            if primary not in is_primary: continue
            if particle not in particles: continue
            if collision not in collisions: continue
            if exit_state not in exit_states: continue

            interactions = dataset[:]
            yield Trajectory(primary, particle, collision, exit_state, interactions)

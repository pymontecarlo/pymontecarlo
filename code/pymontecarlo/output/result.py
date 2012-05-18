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
import bisect
from math import sqrt
from collections import Iterable
from StringIO import StringIO
from xml.etree.ElementTree import Element, tostring, fromstring

# Third party modules.

# Local modules.
from pymontecarlo.util.transition import from_string
from pymontecarlo.output.manager import ResultManager

# Globals and constants variables.
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
            _check2(transition, data, GENERATED, 'generated', NOFLUORESCENCE, 'total')

            _check2(transition, data, EMITTED, 'emitted', CHARACTERISTIC, 'characteristic')
            _check2(transition, data, EMITTED, 'emitted', BREMSSTRAHLUNG, 'bremsstrahlung')
            _check2(transition, data, EMITTED, 'emitted', NOFLUORESCENCE, 'no fluorescence')
            _check2(transition, data, EMITTED, 'emitted', NOFLUORESCENCE, 'total')

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
            if hasattr(transition, 'energy'):
                row.append(transition.energy)
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
        Returns the intensity (and its uncertainty) in counts / (sr.A).
        
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
        produced by fluorescence of primary photons in counts / (sr.A).
        
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
        produced by fluorescence of primary photons in counts / (sr.A).
        
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
        contribution to the total intensity in counts / (sr.A).
        
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
        contribution to the total intensity in counts / (sr.A).
        
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
        Returns the total intensity and its uncertainty for the specified 
        energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the 
        spectrum.
    
        :arg energy_eV: energy of interest (in eV).
        """
        return self._get_intensity(energy_eV, self._total, self._total_unc)

    def background_intensity(self, energy_eV):
        """
        Returns the background intensity and its uncertainty for the specified 
        energy.
        Returns ``(0.0, 0.0)`` if the energy in outside the range of the 
        spectrum.
    
        :arg energy_eV: energy of interest (in eV).
        """
        return self._get_intensity(energy_eV, self._background, self._background_unc)

ResultManager.register('PhotonSpectrumResult', PhotonSpectrumResult)

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

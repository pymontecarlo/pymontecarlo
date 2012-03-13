#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- Common results
================================================================================

.. module:: result
   :synopsis: Common results

.. inheritance-diagram:: result

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import csv
from math import sqrt
from collections import Iterable
from StringIO import StringIO
from xml.etree.ElementTree import Element, tostring, fromstring

# Third party modules.

# Local modules.
from pymontecarlo.util.transition import from_string
from pymontecarlo.result.base.manager import ResultsManager, Result

# Globals and constants variables.
GENERATED = "g"
EMITTED = "e"
NOFLUORESCENCE = "nf"
CHARACTERISTIC = "cf"
BREMSSTRAHLUNG = "bf"
TOTAL = "t"

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

class PhotonIntensityResult(Result):
    _COLUMNS = ['transition', 'energy (eV)',
                'generated characteristic', 'generated characteristic unc',
                'generated bremsstrahlung', 'generated bremsstrahlung unc',
                'generated no fluorescence', 'generated no fluorescence unc',
                'generated total', 'generated total unc',
                'emitted characteristic', 'emitted characteristic unc',
                'emitted bremsstrahlung', 'emitted bremsstrahlung unc',
                'emitted no fluorescence', 'emitted no fluorescence unc',
                'emitted total', 'emitted total unc']

    def __init__(self, detector, intensities={}):
        """
        Creates a new result to store photon intensities.
        
        :arg detector: photon intensity detector
        :arg intensities: :class:`dict` containing the intensities.
            One should use :func:`.create_intensity_dict` to create the dictionary
        """
        Result.__init__(self, detector)

        self._intensities = intensities

    @classmethod
    def __loadzip__(cls, zipfile, key, detector):
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

        return cls(detector, intensities)

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
            >>> result.intensity('Al K')[0]
            
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

ResultsManager.register('PhotonIntensityResult', PhotonIntensityResult)
ResultsManager.register_loader('pymontecarlo.result.base.result.PhotonIntensityResult', PhotonIntensityResult)

class TimeResult(Result):

    def __init__(self, detector, simulation_time_s=0.0, simulation_speed_s=(0.0, 0.0)):
        """
        Creates a new result to store simulation time and speed.
        
        :arg detector: time detector
        :arg simulation_time_s: total time of the simulation (in seconds)
        :arg simulation_speed_s: time to simulation one electron (in seconds) and
            its uncertainty
        """
        Result.__init__(self, detector)

        self._simulation_time_s = simulation_time_s
        self._simulation_speed_s = simulation_speed_s

    @classmethod
    def __loadzip__(cls, zipfile, key, detector):
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

        return cls(detector, simulation_time, simulation_speed)

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

ResultsManager.register('TimeResult', TimeResult)
ResultsManager.register_loader('pymontecarlo.result.base.result.TimeResult', TimeResult)

class ElectronFractionResult(Result):

    def __init__(self, detector,
                 absorbed=(0.0, 0.0),
                 backscattered=(0.0, 0.0),
                 transmitted=(0.0, 0.0)):
        Result.__init__(self, detector)

        self._absorbed = absorbed
        self._backscattered = backscattered
        self._transmitted = transmitted

    @classmethod
    def __loadzip__(cls, zipfile, key, detector):
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

        return cls(detector, absorbed, backscattered, transmitted)

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

ResultsManager.register('ElectronFractionResult', ElectronFractionResult)
ResultsManager.register_loader('pymontecarlo.result.base.result.ElectronFractionResult', ElectronFractionResult)

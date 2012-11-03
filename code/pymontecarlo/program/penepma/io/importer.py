#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- PENEPMA importer
================================================================================

.. module:: importer
   :synopsis: PENEPMA importer

.. inheritance-diagram:: pymontecarlo.program.penepma.io.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import glob
from itertools import izip
from collections import defaultdict

# Third party modules.

# Local modules.
from pymontecarlo.output.result import \
    (
    PhotonIntensityResult,
    PhotonSpectrumResult,
    ElectronFractionResult,
    TimeResult,
    ShowersStatisticsResult,
    PhiRhoZResult,
    create_intensity_dict,
    create_phirhoz_dict,
    )
from pymontecarlo.input.detector import \
    (
     _PhotonDelimitedDetector,
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
     PhotonSpectrumDetector,
     PhotonIntensityDetector,
     ElectronFractionDetector,
     TimeDetector,
     ShowersStatisticsDetector,
     )
from pymontecarlo.util.transition import Transition
from pymontecarlo.program._penelope.io.importer import \
    Importer as _Importer, ImporterException
from pymontecarlo.program.penepma.input.detector import index_delimited_detectors

# Globals and constants variables.
from pymontecarlo.output.result import \
    EMITTED, NOFLUORESCENCE, CHARACTERISTIC, BREMSSTRAHLUNG, TOTAL

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonSpectrumDetector] = \
            self._detector_photon_spectrum
        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_importers[PhiRhoZDetector] = \
            self._detector_phirhoz
        self._detector_importers[ElectronFractionDetector] = \
            self._detector_electron_fraction
        self._detector_importers[TimeDetector] = self._detector_time
        self._detector_importers[ShowersStatisticsDetector] = \
            self._detector_showers_statistics

    def _import_results(self, options, path, *args):
        # Find index for each delimited detector
        # The same method (index_delimited_detectors) is called when exporting
        # the result. It ensures that the same index is used for all detectors
        dets = options.detectors.findall(_PhotonDelimitedDetector)
        phdets_key_index, phdets_index_keys = index_delimited_detectors(dets)

        return _Importer._import_results(self, options, path,
                                         phdets_key_index, phdets_index_keys,
                                         *args)

    def _detector_photon_spectrum(self, options, key, detector, path,
                                  phdets_key_index, phdets_index_keys, *args):
        index = phdets_key_index[key] + 1

        # Find data files
        charact_filepath = os.path.join(path, 'pe-charact-%s.dat' % str(index).zfill(2))
        if not os.path.exists(charact_filepath):
            raise ImporterException, "Data file %s cannot be found" % charact_filepath

        spect_filepath = os.path.join(path, 'pe-spect-%s.dat' % str(index).zfill(2))
        if not os.path.exists(spect_filepath):
            raise ImporterException, "Data file %s cannot be found" % spect_filepath

        # Load characteristic spectrum
        charact = []
        charact_unc = []

        with open(charact_filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('#'): continue
                values = line.split()

                charact.append(float(values[1]))
                charact_unc.append(float(values[2]))

        # Load total spectrum
        energies = []
        total = []
        total_unc = []

        with open(spect_filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('#'): continue
                values = line.split()

                energies.append(float(values[0]))
                total.append(float(values[1]))
                total_unc.append(float(values[2]))

        # Calculate background
        background = [t - c for t, c in izip(total, charact)]
        background_unc = [t + c for t, c in izip(total_unc, charact_unc)]

        # Process
        energy_channel_width_eV = energies[1] - energies[0]
        energy_offset_eV = energies[0] - energy_channel_width_eV / 2.0

        return PhotonSpectrumResult(energy_offset_eV, energy_channel_width_eV,
                                    total, total_unc, background, background_unc)

    def _detector_photon_intensity(self, options, key, detector, path,
                                   phdets_key_index, phdets_index_keys, *args):
        def _read_intensities_line(line):
            values = line.split()

            try:
                transition = Transition(z=int(values[0]),
                                        src=int(values[2]),
                                        dest=int(values[1]))
            except ValueError: # transition not supported
                return None, 0.0, 0.0, 0.0, 0.0

            nf = float(values[4]), float(values[5])
            cf = float(values[6]), float(values[7])
            bf = float(values[8]), float(values[9])
            #tf = float(values[10]), float(values[11]) # skip not needed
            t = float(values[12]), float(values[13])

            return transition, cf, bf, nf, t

        index = phdets_key_index[key] + 1

        # Find data files
        emitted_filepath = os.path.join(path, 'pe-inten-%s.dat' % str(index).zfill(2))
        if not os.path.exists(emitted_filepath):
            raise ImporterException, "Data file %s cannot be found" % emitted_filepath

        generated_filepath = os.path.join(path, 'pe-gen-ph.dat')
        if not os.path.exists(generated_filepath):
            raise ImporterException, "Data file %s cannot be found" % generated_filepath

        # Load generated
        intensities = {}

        with open(generated_filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('#'): continue

                transition, gcf, gbf, gnf, gt = _read_intensities_line(line)

                if transition is not None:
                    tmpintensities = \
                        create_intensity_dict(transition, gcf, gbf, gnf, gt)
                    intensities.update(tmpintensities)

        # Load emitted
        with open(emitted_filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('#'): continue

                transition, ecf, ebf, enf, et = _read_intensities_line(line)

                if transition is not None:
                    tmpintensities = intensities[transition]
                    tmpintensities[EMITTED][CHARACTERISTIC] = ecf
                    tmpintensities[EMITTED][BREMSSTRAHLUNG] = ebf
                    tmpintensities[EMITTED][NOFLUORESCENCE] = enf
                    tmpintensities[EMITTED][TOTAL] = et

        return PhotonIntensityResult(intensities)

    def _detector_phirhoz(self, options, key, detector, path,
                          phdets_key_index, phdets_index_keys, *args):
        index = phdets_key_index[key] + 1

        # Find data files
        pattern = os.path.join(path, 'pe-prz-*-%s.dat' % str(index).zfill(2))
        filepaths = glob.glob(pattern)

        # Load distributions
        distributions = {}

        for filepath in filepaths:
            # Transition
            code = os.path.basename(filepath)[7:13]
            z = int(code[:2])
            dest = int(code[2:4])
            src = int(code[4:6])
            transition = Transition(z, src, dest)

            # Read data
            data = defaultdict(list)
            with open(filepath, 'r') as fp:
                for line in fp:
                    line = line.strip()
                    if line.startswith('#'): continue
                    values = line.split()

                    data['zs'].append(float(values[0]))
                    data['zfs'].append(float(values[1]))
                    data['gnf'].append(float(values[4]))
                    data['gnf_unc'].append(float(values[5]))
                    data['gt'].append(float(values[20]))
                    data['gt_unc'].append(float(values[21]))
                    data['enf'].append(float(values[2]))
                    data['enf_unc'].append(float(values[3]))
                    data['et'].append(float(values[18]))
                    data['et_unc'].append(float(values[19]))

            # Convert units of depth
            data['zs'] = [-z * 1e-2 for z in data['zs']]
            data['zfs'] = [-z * 1e-2 for z in data['zfs']]

            # Reverse all data to have increase z values
            for value in data.itervalues():
                value.reverse()

            # Assemble data
            gnf = data['zs'], data['gnf'], data['gnf_unc']
            gt = data['zfs'], data['gt'], data['gt_unc']
            enf = data['zs'], data['enf'], data['enf_unc']
            et = data['zfs'], data['et'], data['et_unc']

            distributions.update(create_phirhoz_dict(transition, gnf, gt, enf, et))

        return PhiRhoZResult(distributions)

    def _read_log(self, path):
        """
        Returns the last line of the :file:`penepma.csv` log file as a 
        :class:`dict` where the keys are the header of each column and the 
        values are the values of the last line.
        
        :arg path: directory containing the simulation files
        """
        filepath = os.path.join(path, 'penepma.csv')
        if not os.path.exists(filepath):
            raise ImporterException, "Data file %s cannot be found" % filepath

        with open(filepath, 'r') as fp:
            header = fp.readline().strip().split(',')
            header = [s.strip() for s in header]
            line = []

            for line in fp:
                continue

        line = line.strip().rstrip(',').split(',')
        values = map(float, line)

        return dict(zip(header, values))

    def _detector_electron_fraction(self, options, key, detector, path, *args):
        line = self._read_log(path)

        absorbed = line['F_ABS'], line['F_ABS_E']
        backscattered = line['F_BSE'], line['F_BSE_E']
        transmitted = line['F_TRANS'], line['F_TRANS_E']

        return ElectronFractionResult(absorbed, backscattered, transmitted)

    def _detector_time(self, options, key, detector, path, *args):
        line = self._read_log(path)

        simulation_time_s = line['SIM_TIME']
        simulation_speed_s = 1.0 / line['SIM_SPEED'], 0.0

        return TimeResult(simulation_time_s, simulation_speed_s)

    def _detector_showers_statistics(self, options, key, detector, path, *args):
        line = self._read_log(path)

        showers = line['N_ELECTRON']

        return ShowersStatisticsResult(showers)

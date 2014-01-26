#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- PENEPMA importer
================================================================================

.. module:: importer
   :synopsis: PENEPMA importer

.. inheritance-diagram:: pymontecarlo.program.penepma.output.importer

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
from collections import defaultdict

# Third party modules.
import numpy as np

from pyxray.transition import Transition

# Local modules.
from pymontecarlo.results.result import \
    (
    PhotonIntensityResult,
    PhotonSpectrumResult,
    ElectronFractionResult,
    TimeResult,
    ShowersStatisticsResult,
    PhotonDepthResult,
    create_intensity_dict,
    create_photondist_dict,
    BackscatteredElectronEnergyResult,
    )
from pymontecarlo.options.detector import \
    (
     _PhotonDelimitedDetector,
     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     PhotonDepthDetector,
     PhotonSpectrumDetector,
     PhotonIntensityDetector,
     ElectronFractionDetector,
     TimeDetector,
     ShowersStatisticsDetector,
     )
from pymontecarlo.program.importer import Importer as _Importer, ImporterException
from pymontecarlo.program.penepma.options.detector import index_delimited_detectors

# Globals and constants variables.
from pymontecarlo.results.result import \
    EMITTED, NOFLUORESCENCE, CHARACTERISTIC, BREMSSTRAHLUNG, TOTAL

def _load_dat_files(filepath):
    bins = []
    vals = []
    uncs = []

    with open(filepath, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line.startswith('#'): continue
            if not line: continue
            values = line.split()

            bins.append(float(values[0]))
            vals.append(float(values[1]))
            uncs.append(float(values[2]))

    return bins, vals, uncs

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._importers[PhotonSpectrumDetector] = \
            self._import_photon_spectrum
        self._importers[PhotonIntensityDetector] = self._import_photon_intensity
        self._importers[PhotonDepthDetector] = self._import_photondepth
        self._importers[ElectronFractionDetector] = \
            self._import_electron_fraction
        self._importers[TimeDetector] = self._import_time
        self._importers[ShowersStatisticsDetector] = \
            self._import_showers_statistics
        self._importers[BackscatteredElectronEnergyDetector] = \
            self._import_backscattered_electron_energy

    def _import(self, options, dirpath, *args, **kwargs):
        # Find index for each delimited detector
        # The same method (index_delimited_detectors) is called when exporting
        # the result. It ensures that the same index is used for all detectors
        dets = dict(options.detectors.iterclass(_PhotonDelimitedDetector))
        phdets_key_index, phdets_index_keys = index_delimited_detectors(dets)

        return self._run_importers(options, dirpath,
                                   phdets_key_index, phdets_index_keys,
                                   *args, **kwargs)

    def _import_photon_spectrum(self, options, key, detector, path,
                                  phdets_key_index, phdets_index_keys, *args):
        index = phdets_key_index[key] + 1

        # Find data files
        charact_filepath = os.path.join(path, 'pe-charact-%s.dat' % str(index).zfill(2))
        if not os.path.exists(charact_filepath):
            raise ImporterException("Data file %s cannot be found" % charact_filepath)

        spect_filepath = os.path.join(path, 'pe-spect-%s.dat' % str(index).zfill(2))
        if not os.path.exists(spect_filepath):
            raise ImporterException("Data file %s cannot be found" % spect_filepath)

        # Load characteristic spectrum
        _, charact_val, charact_unc = _load_dat_files(charact_filepath)

        # Load total spectrum
        energies, total_val, total_unc = _load_dat_files(spect_filepath)

        # Calculate background
        background_val = [t - c for t, c in zip(total_val, charact_val)]
        background_unc = [t + c for t, c in zip(total_unc, charact_unc)]

        # Process
        total = np.array([energies, total_val, total_unc]).T
        background = np.array([energies, background_val, background_unc]).T

        return PhotonSpectrumResult(total, background)

    def _import_photon_intensity(self, options, key, detector, path,
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
            raise ImporterException("Data file %s cannot be found" % emitted_filepath)

        generated_filepath = os.path.join(path, 'pe-gen-ph.dat')
        if not os.path.exists(generated_filepath):
            raise ImporterException("Data file %s cannot be found" % generated_filepath)

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

    def _import_photondepth(self, options, key, detector, path,
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
            for value in data.values():
                value.reverse()

            # Assemble data
            gnf = np.array([data['zs'], data['gnf'], data['gnf_unc']]).T
            gt = np.array([data['zfs'], data['gt'], data['gt_unc']]).T
            enf = np.array([data['zs'], data['enf'], data['enf_unc']]).T
            et = np.array([data['zfs'], data['et'], data['et_unc']]).T

            distributions.update(create_photondist_dict(transition, gnf, gt, enf, et))

        return PhotonDepthResult(distributions)

    def _read_log(self, path):
        """
        Returns the last line of the :file:`penepma.csv` log file as a
        :class:`dict` where the keys are the header of each column and the
        values are the values of the last line.

        :arg path: directory containing the simulation files
        """
        filepath = os.path.join(path, 'penepma.csv')
        if not os.path.exists(filepath):
            raise ImporterException("Data file %s cannot be found" % filepath)

        with open(filepath, 'r') as fp:
            header = fp.readline().strip().split(',')
            header = [s.strip() for s in header]
            line = []

            for line in fp:
                continue

        line = line.strip().rstrip(',').split(',')
        values = map(float, line)

        return dict(zip(header, values))

    def _import_electron_fraction(self, options, key, detector, path, *args):
        line = self._read_log(path)

        absorbed = line['F_ABS'], line['F_ABS_E']
        backscattered = line['F_BSE'], line['F_BSE_E']
        transmitted = line['F_TRANS'], line['F_TRANS_E']

        return ElectronFractionResult(absorbed, backscattered, transmitted)

    def _import_time(self, options, key, detector, path, *args):
        line = self._read_log(path)

        simulation_time_s = line['SIM_TIME']
        simulation_speed_s = 1.0 / line['SIM_SPEED'], 0.0

        return TimeResult(simulation_time_s, simulation_speed_s)

    def _import_showers_statistics(self, options, key, detector, path, *args):
        line = self._read_log(path)

        showers = line['N_ELECTRON']

        return ShowersStatisticsResult(showers)

    def _import_backscattered_electron_energy(self, options, key, detector, path, *args):
        filepath = os.path.join(path, 'pe-energy-el-back.dat')
        if not os.path.exists(filepath):
            raise ImporterException("Data file %s cannot be found" % filepath)

        # Load distributions
        bins, vals, uncs = _load_dat_files(filepath)
        data = np.array([bins, vals, uncs]).T

        return BackscatteredElectronEnergyResult(data)

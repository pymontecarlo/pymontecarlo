#!/usr/bin/env python
"""
================================================================================
:mod:`updater` -- Results updater
================================================================================

.. module:: updater
   :synopsis: Results updater

.. inheritance-diagram:: pymontecarlo.output.updater

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import csv
import logging
import tempfile
import shutil
from StringIO import StringIO
from zipfile import ZipFile, is_zipfile
from xml.etree.ElementTree import fromstring

# Third party modules.
import h5py
import numpy as np

# Local modules.
from pymontecarlo.util.updater import _Updater
from pymontecarlo.util.config import ConfigParser
from pymontecarlo.util.transition import from_string

from pymontecarlo.input.options import Options

from pymontecarlo.output.results import Results
from pymontecarlo.output.result import \
    (PhotonIntensityResult, create_intensity_dict, PhotonSpectrumResult,
     PhiRhoZResult, create_phirhoz_dict, TimeResult, ShowersStatisticsResult,
     ElectronFractionResult, BackscatteredElectronEnergyResult,
     TransmittedElectronEnergyResult, Trajectory, TrajectoryResult)

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

from pymontecarlo.input.particle import PARTICLES
from pymontecarlo.input.collision import COLLISIONS

SECTION_KEYS = 'keys'
KEYS_INI_FILENAME = 'keys.ini'
OPTIONS_FILENAME = 'options.xml'

class Updater(_Updater):

    def __init__(self):
        """
        Creates a new updater for the results.
        """
        _Updater.__init__(self)

        self._updaters[0] = self._update_noversion
        self._updaters[2] = self._update_version2
        self._updaters[3] = self._update_version3
        self._updaters[4] = self._update_version4
        self._updaters[5] = self._update_version5

    def _get_version(self, filepath):
        if is_zipfile(filepath):
            with ZipFile(filepath, 'r') as zip:
                comment = zip.comment

            try:
                return int(comment.split('=')[1])
            except:
                return 0
        else:
            hdf5file = h5py.File(filepath, 'r')
            version = int(hdf5file.attrs['version'])
            hdf5file.close()
            return version

    def _validate(self, filepath):
        Results.load(filepath)

    def _update_noversion(self, filepath):
        logging.debug('Updating from "no version"')

        oldzip = ZipFile(filepath, 'r')
        newzip = ZipFile(filepath + ".new", 'w')

        # Update keys.ini
        config = ConfigParser()
        config.read(oldzip.open(KEYS_INI_FILENAME, 'r'))

        for section, option, value in config:
            value = value.replace('pymontecarlo.result.base.result.', '')
            setattr(getattr(config, section), option, value)

        fp = StringIO()
        config.write(fp)
        newzip.writestr(KEYS_INI_FILENAME, fp.getvalue())

        # Add other files to new zip
        for zipinfo in oldzip.infolist():
            if zipinfo.filename == KEYS_INI_FILENAME:
                continue

            data = oldzip.read(zipinfo)
            newzip.writestr(zipinfo, data)

        # Add version
        newzip.comment = 'version=%s' % '2'

        oldzip.close()
        newzip.close()

        # Remove old zip and replace with new one
        os.remove(filepath)
        os.rename(filepath + ".new", filepath)

        return self._update_version2(filepath)

    def _update_version2(self, filepath):
        logging.debug('Updating from "version 2"')

        # Find options
        xmlfilepath = os.path.splitext(filepath)[0] + '.xml'
        if not os.path.exists(xmlfilepath):
            raise ValueError, 'Update requires an options file saved at %s' % xmlfilepath
        options = Options.load(xmlfilepath)

        oldzip = ZipFile(filepath, 'r')
        newzip = ZipFile(filepath + ".new", 'w')

        # Add options file
        fp = StringIO()
        options.save(fp)
        newzip.writestr(OPTIONS_FILENAME, fp.getvalue())

        # Add other files to new zip
        for zipinfo in oldzip.infolist():
            data = oldzip.read(zipinfo)
            newzip.writestr(zipinfo, data)

        # Add version
        newzip.comment = 'version=%s' % '3'

        oldzip.close()
        newzip.close()

        # Remove old zip and replace with new one
        os.remove(filepath)
        os.rename(filepath + ".new", filepath)

        return self._update_version3(filepath)

    def _update_version3(self, filepath):
        logging.debug('Updating from "version 3"')

        manager = {}

        def _load_photonintensity(zipfile, key):
            reader = csv.reader(zipfile.open(key + '.csv', 'r'))
            reader.next()

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

            return PhotonIntensityResult(intensities)

        manager['PhotonIntensityResult'] = _load_photonintensity

        def _load_photonspectrum(zipfile, key):
            reader = csv.reader(zipfile.open(key + '.csv', 'r'))
            reader.next()

            energies_eV = []
            total_val = []
            total_unc = []
            background_val = []
            background_unc = []
            for row in reader:
                energies_eV.append(float(row[0]))
                total_val.append(float(row[1]))
                total_unc.append(float(row[2]))
                background_val.append(float(row[3]))
                background_unc.append(float(row[4]))

            total = np.array([energies_eV, total_val, total_unc]).T
            background = np.array([energies_eV, background_val, background_unc]).T

            return PhotonSpectrumResult(total, background)

        manager['PhotonSpectrumResult'] = _load_photonspectrum

        def _load_phirhoz(zipfile, key):
            # Find all phi-rho-z files
            arcnames = [name for name in zipfile.namelist() if name.startswith(key)]

            # Read files
            data = {}
            for arcname in arcnames:
                parts = os.path.splitext(arcname)[0].split('+')
                transition = from_string(parts[-2].replace('_', ' '))
                suffix = parts[-1]

                reader = csv.reader(zipfile.open(arcname, 'r'))
                reader.next()

                zs = []
                values = []
                uncs = []
                for row in reader:
                    zs.append(float(row[0]))
                    values.append(float(row[1]))
                    uncs.append(float(row[2]))

                datum = np.array([zs, values, uncs]).T
                data.setdefault(transition, {})[suffix] = datum

            # Construct distributions
            distributions = {}
            for transition, datum in data.iteritems():
                distributions.update(create_phirhoz_dict(transition, **datum))

            return PhiRhoZResult(distributions)

        manager['PhiRhoZResult'] = _load_phirhoz

        def _load_time(zipfile, key):
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

            return TimeResult(simulation_time, simulation_speed)

        manager['TimeResult'] = _load_time

        def _load_showersstatistics(zipfile, key):
            element = fromstring(zipfile.open(key + '.xml', 'r').read())

            child = element.find('showers')
            if child is not None:
                showers = float(child.get('val', 0))
            else:
                showers = 0

            return ShowersStatisticsResult(showers)

        manager['ShowersStatisticsResult'] = _load_showersstatistics

        def _load_electronfraction(zipfile, key):
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

            return ElectronFractionResult(absorbed, backscattered, transmitted)

        manager['ElectronFractionResult'] = _load_electronfraction

        def _load_trajectory(zipfile, key):
            tmpdir = tempfile.mkdtemp()
            filename = key + '.h5'
            zipfile.extract(filename, tmpdir)

            hdf5file = h5py.File(os.path.join(tmpdir, filename))

            particles_ref = list(PARTICLES)
            particles_ref = dict(zip(map(str, particles_ref), particles_ref))

            collisions_ref = list(COLLISIONS)
            collisions_ref = dict(zip(map(str, collisions_ref), collisions_ref))

            trajectories = []

            for dataset in hdf5file['trajectories'].itervalues():
                primary = bool(dataset.attrs['primary'])
                particle = particles_ref.get(dataset.attrs['particle'])
                collision = collisions_ref.get(dataset.attrs['collision'])
                exit_state = int(dataset.attrs['exit_state'])
                interactions = dataset[:]

                trajectory = Trajectory(primary, particle, collision,
                                        exit_state, interactions)
                trajectories.append(trajectory)

            hdf5file.close()
            shutil.rmtree(tmpdir, ignore_errors=True)

            return TrajectoryResult(trajectories)

        manager['TrajectoryResult'] = _load_trajectory

        def _load_backscatteredelectronenergy(zipfile, key):
            data = np.loadtxt(zipfile.open(key + '.csv', 'r'), delimiter=',')
            return BackscatteredElectronEnergyResult(data)

        manager['BackscatteredElectronEnergyResult'] = _load_backscatteredelectronenergy

        def _load_transmittedelectronenergy(zipfile, key):
            data = np.loadtxt(zipfile.open(key + '.csv', 'r'), delimiter=',')
            return TransmittedElectronEnergyResult(data)

        manager['TransmittedElectronEnergyResult'] = _load_transmittedelectronenergy

        def _load_results(filepath):
            zipfile = ZipFile(filepath, 'r', allowZip64=True)

            # Read options
            try:
                zipinfo = zipfile.getinfo(OPTIONS_FILENAME)
            except KeyError:
                raise IOError, "Zip file (%s) does not contain a %s" % \
                        (filepath, OPTIONS_FILENAME)

            options = Options.load(zipfile.open(zipinfo, 'r'))

            # Parse keys.ini
            try:
                zipinfo = zipfile.getinfo(KEYS_INI_FILENAME)
            except KeyError:
                raise IOError, "Zip file (%s) does not contain a %s" % \
                        (filepath, KEYS_INI_FILENAME)

            config = ConfigParser()
            config.read(zipfile.open(zipinfo, 'r'))

            # Load each results
            items = list(getattr(config, SECTION_KEYS))

            results = {}
            for key, tag in items:
                loader = manager[tag]
                results[key] = loader(zipfile, key)

            zipfile.close()

            return Results(options, results)

        # Update results
        results = _load_results(filepath)

        newfilepath = os.path.splitext(filepath)[0] + '.h5'
        results.save(newfilepath)

        # Create raw ZIP
        oldzip = ZipFile(filepath, 'r')

        if any([filename.startswith('raw/') for filename in oldzip.namelist()]):
            zipfilepath = os.path.splitext(filepath)[0] + '_raw.zip'
            newzip = ZipFile(zipfilepath, 'w', compression=ZIP_DEFLATED)

            for filename in oldzip.namelist():
                if not filename.startswith('raw/'): continue
                data = oldzip.read(filename)
                newzip.writestr(filename[4:], data)

            newzip.close()

        oldzip.close()

        return self._update_version4(newfilepath)

    def _update_version4(self, filepath):
        """
        Update structure of PRZ results in HDF5.
        """
        hdf5file = h5py.File(filepath, 'r+')

        # Find PRZ result (if any)
        przgroups = []

        for result_group in hdf5file.itervalues():
            if result_group.attrs.get('_class') == 'PhiRhoZResult':
                przgroups.append(result_group)

        # Convert datasets
        for przgroup in przgroups:
            for name, dataset in przgroup.items():
                if '+' not in name:
                    continue

                transition, suffix = name.split('+')

                tgroup = przgroup.require_group(transition)
                tgroup.create_dataset(suffix, data=np.copy(dataset))

                del przgroup[name] # delete dataset

        # Change version
        hdf5file.attrs['version'] = '5'

        hdf5file.close()

        return self._update_version5(filepath)

    def _update_version5(self, filepath):
        logging.info('Nothing to update')
        return filepath

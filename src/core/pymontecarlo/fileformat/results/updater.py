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
from io import BytesIO, StringIO
from zipfile import ZipFile, is_zipfile

# Third party modules.
import h5py

import numpy as np

from pyxray.transition import from_string

# Local modules.
from pymontecarlo.util.updater import _Updater
from pymontecarlo.util.config import ConfigParser
import pymontecarlo.util.hdf5util as hdf5util
import pymontecarlo.util.xmlutil as xmlutil

from pymontecarlo.fileformat.options.updater import Updater as OptionsUpdater
from pymontecarlo.fileformat.options.options import \
    load as load_options, save as save_options
from pymontecarlo.fileformat.results.results import load as load_results
from pymontecarlo.fileformat.handler import find_convert_handler

from pymontecarlo.results.result import \
    (PhotonIntensityResult, create_intensity_dict, PhotonSpectrumResult,
     PhotonDepthResult, create_photondist_dict, TimeResult, ShowersStatisticsResult,
     ElectronFractionResult, BackscatteredElectronEnergyResult,
     TransmittedElectronEnergyResult, Trajectory, TrajectoryResult)

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

from pymontecarlo.options.particle import PARTICLES
from pymontecarlo.options.collision import COLLISIONS

SECTION_KEYS = 'keys'
KEYS_INI_FILENAME = 'keys.ini'
OPTIONS_FILENAME = 'options.xml'

def _update_options(source):
    logging.info('Update options')

    # Open temporary file and write options in it.
    fd, tmpfilepath = tempfile.mkstemp('.xml')
    with open(tmpfilepath, 'wb') as fp:
        fp.write(source)

    # Update
    OptionsUpdater().update(tmpfilepath)

    # Read options and update HDF5
    with open(tmpfilepath, 'rb') as fp:
        source = fp.read()

    # Close temporary file and remove it
    os.close(fd)
    os.remove(tmpfilepath)
    os.remove(tmpfilepath + '.bak')

    return source

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
        self._updaters[6] = self._update_version6
        self._updaters[7] = self._update_version7

    def _get_version(self, filepath):
        if is_zipfile(filepath):
            with ZipFile(filepath, 'r') as z:
                comment = z.comment.decode('ascii')

            try:
                return int(comment.split('=')[1])
            except:
                return 0
        elif os.path.splitext(filepath)[1] == '.h5':
            hdf5file = h5py.File(filepath, 'r')
            version = int(hdf5file.attrs['version'])
            hdf5file.close()
            return version
        else:
            raise ValueError("Unknown file format: %s" % filepath)

    def _make_backup(self, filepath):
        bak_filepath = _Updater._make_backup(self, filepath)
        if os.path.splitext(filepath)[1] != '.h5':
            return bak_filepath

        # Special check for HDF5 file created in Java
        # The HDF5 has to be re-saved to allow modifications
        hdf5file_original = h5py.File(bak_filepath, 'r+')

        try:
            hdf5file_original.attrs['version'] = hdf5file_original.attrs['version']
        except:
            hdf5file_copy = h5py.File(filepath, 'w')
            hdf5util.copy(hdf5file_original, hdf5file_copy)
            hdf5file_copy.close()
        finally:
            hdf5file_original.close()

        return bak_filepath

    def _validate(self, filepath):
        load_results(filepath)

    def _update_noversion(self, filepath):
        logging.debug('Updating from "no version"')

        oldzip = ZipFile(filepath, 'r')
        newzip = ZipFile(filepath + ".new", 'w')

        # Update keys.ini
        config = ConfigParser()

        fp = oldzip.open(KEYS_INI_FILENAME, 'r')
        config.read(StringIO(fp.read().decode('ascii')))

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
        newzip.comment = b'version=2'

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
            raise ValueError('Update requires an options file saved at %s' % xmlfilepath)
        with open(xmlfilepath, 'rb') as fp:
            source = fp.read()
        source = _update_options(source)
        options = load_options(BytesIO(source))

        oldzip = ZipFile(filepath, 'r')
        newzip = ZipFile(filepath + ".new", 'w')

        # Add options file
        fp = BytesIO()
        save_options(options, fp)
        newzip.writestr(OPTIONS_FILENAME, fp.getvalue())

        # Add other files to new zip
        for zipinfo in oldzip.infolist():
            data = oldzip.read(zipinfo)
            newzip.writestr(zipinfo, data)

        # Add version
        newzip.comment = b'version=3'

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
            fp = zipfile.open(key + '.csv', 'r')
            reader = csv.reader(StringIO(fp.read().decode('ascii')))
            next(reader)

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
            fp = zipfile.open(key + '.csv', 'r')
            reader = csv.reader(StringIO(fp.read().decode('ascii')))
            next(reader)

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

                fp = zipfile.open(arcname, 'r')
                reader = csv.reader(StringIO(fp.read().decode('ascii')))
                next(reader)

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
            for transition, datum in data.items():
                distributions.update(create_photondist_dict(transition, **datum))

            return PhotonDepthResult(distributions)

        manager['PhiRhoZResult'] = _load_phirhoz

        def _load_time(zipfile, key):
            element = xmlutil.parse(zipfile.open(key + '.xml', 'r'))

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
            element = xmlutil.parse(zipfile.open(key + '.xml', 'r').read())

            child = element.find('showers')
            if child is not None:
                showers = float(child.get('val', 0))
            else:
                showers = 0

            return ShowersStatisticsResult(showers)

        manager['ShowersStatisticsResult'] = _load_showersstatistics

        def _load_electronfraction(zipfile, key):
            element = xmlutil.parse(zipfile.open(key + '.xml', 'r'))

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

            for dataset in hdf5file['trajectories'].values():
                primary = bool(dataset.attrs['primary'])
                particle = particles_ref.get(dataset.attrs['particle'].decode('ascii'))
                collision = collisions_ref.get(dataset.attrs['collision'].decode('ascii'))
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

        # Create HDF5
        newfilepath = os.path.splitext(filepath)[0] + '.h5'
        hdf5file = h5py.File(newfilepath, 'w')
        hdf5file.attrs['version'] = b'4'

        zipfile = ZipFile(filepath, 'r', allowZip64=True)

        ## Read options
        try:
            zipinfo = zipfile.getinfo(OPTIONS_FILENAME)
        except KeyError:
            raise IOError("Zip file (%s) does not contain a %s" % \
                          (filepath, OPTIONS_FILENAME))
        with zipfile.open(zipinfo, 'r') as fp:
            source = fp.read()
        source = _update_options(source)
        hdf5file.attrs['options'] = source

        ## Parse keys.ini
        try:
            zipinfo = zipfile.getinfo(KEYS_INI_FILENAME)
        except KeyError:
            raise IOError("Zip file (%s) does not contain a %s" % \
                          (filepath, KEYS_INI_FILENAME))

        config = ConfigParser()
        config.read(StringIO(zipfile.open(zipinfo, 'r').read().decode('ascii')))

        ## Load each results
        items = list(getattr(config, SECTION_KEYS))

        for key, tag in items:
            loader = manager[tag]
            result = loader(zipfile, key)

            handler = find_convert_handler('pymontecarlo.fileformat.results.result', result)

            group = hdf5file.create_group(key)
            handler.convert(result, group)

        zipfile.close()
        hdf5file.close()

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
        logging.debug('Updating from "version 4"')

        hdf5file = h5py.File(filepath, 'r+')

        # Find PRZ result (if any)
        przgroups = []

        for result_group in hdf5file.values():
            if result_group.attrs.get('_class') == b'PhiRhoZResult':
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
        hdf5file.attrs['version'] = b'5'

        hdf5file.close()

        return self._update_version5(filepath)

    def _update_version5(self, filepath):
        logging.debug('Updating from "version 5"')

        hdf5file = h5py.File(filepath, 'r+')

        hdf5file.attrs['version'] = b'6' # Change version

        for result_group in hdf5file.values():
            if result_group.attrs.get('_class') == b'PhiRhoZResult':
                result_group.attrs['_class'] = 'PhotonDepthResult'

        # Options
        source = _update_options(hdf5file.attrs['options'])
        hdf5file.attrs['options'] = source

        hdf5file.close()

        return self._update_version6(filepath)

    def _update_version6(self, filepath):
        logging.debug('Updating from "version 6"')

        hdf5file = h5py.File(filepath, 'r+')

        hdf5file.attrs['version'] = b'7' # Change version
        hdf5file.attrs['_class'] = b'Results'

        # Update root options
        options_source = _update_options(hdf5file.attrs['options'])
        hdf5file.attrs['options'] = options_source

        # Create identifier of results
        identifier = load_options(BytesIO(options_source)).uuid
        hdf5file.attrs.create('identifiers', [identifier],
                              dtype=h5py.special_dtype(vlen=str))

        result_groups = list(hdf5file)
        group = hdf5file.create_group(identifier)
        group.attrs['options'] = options_source

        for result_group in result_groups:
            hdf5file[result_group].attrs['_class'] = \
                np.string_(hdf5file[result_group].attrs['_class'])
            hdf5file.copy(result_group, group)
            del hdf5file[result_group]

        hdf5file.close()

        return self._update_version7(filepath)

    def _update_version7(self, filepath):
        logging.info('Nothing to update')
        return filepath



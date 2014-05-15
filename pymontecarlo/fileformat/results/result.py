#!/usr/bin/env python
"""
================================================================================
:mod:`result` -- HDF5 handler for results
================================================================================

.. module:: result
   :synopsis: HDF5 handler for results

.. inheritance-diagram:: pymontecarlo.fileformat.results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import pyxray.transition as xraytransition
import numpy as np

# Local modules.
from pymontecarlo.fileformat.hdf5handler import _HDF5Handler

from pymontecarlo.results.result import \
    (PhotonKey, PhotonIntensityResult, PhotonSpectrumResult,
     _PhotonDistributionResult, create_photondist_dict, PhotonDepthResult,
     PhotonRadialResult,
     TimeResult, ShowersStatisticsResult, ElectronFractionResult,
     TrajectoryResult, Trajectory,
     _ChannelsResult, BackscatteredElectronEnergyResult,
     TransmittedElectronEnergyResult, BackscatteredElectronPolarAngularResult,
     BackscatteredElectronRadialResult)

# Globals and constants variables.
from pymontecarlo.options.particle import PARTICLES
from pymontecarlo.options.collision import COLLISIONS

class PhotonIntensityResultHDF5Handler(_HDF5Handler):

    CLASS = PhotonIntensityResult

    def parse(self, group):
        intensities = {}

        for transition, dataset in group.items():
            transition = xraytransition.from_string(transition)

            intensities[PhotonKey(transition, False, PhotonKey.P)] = dataset.attrs['gnf']
            intensities[PhotonKey(transition, False, PhotonKey.C)] = dataset.attrs['gcf']
            intensities[PhotonKey(transition, False, PhotonKey.B)] = dataset.attrs['gbf']
            intensities[PhotonKey(transition, True, PhotonKey.P)] = dataset.attrs['enf']
            intensities[PhotonKey(transition, True, PhotonKey.C)] = dataset.attrs['ecf']
            intensities[PhotonKey(transition, True, PhotonKey.B)] = dataset.attrs['ebf']

        return PhotonIntensityResult(intensities)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)

        for key, intensity in obj._intensities.items():
            transition = key.transition
            name = '%s %s' % (transition.symbol, transition.iupac)
            dataset = group.require_dataset(name, shape=(), dtype=np.float)

            attrname = 'g' if key.is_generated() else 'e'
            if key.flag == PhotonKey.PRIMARY:
                attrname += 'nf'
            elif key.flag == PhotonKey.CHARACTERISTIC_FLUORESCENCE:
                attrname += 'cf'
            elif key.flag == PhotonKey.BREMSSTRAHLUNG_FLUORESCENCE:
                attrname += 'bf'

            dataset.attrs[attrname] = intensity[0]

        return group

class PhotonSpectrumResultHDF5Handler(_HDF5Handler):

    CLASS = PhotonSpectrumResult

    def parse(self, group):
        total = np.copy(group['total'])
        background = np.copy(group['background'])
        return PhotonSpectrumResult(total, background)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)
        group.create_dataset('total', data=obj.get_total())
        group.create_dataset('background', data=obj.get_background())
        return group

class _PhotonDistributionResultHDF5Handler(_HDF5Handler):

    CLASS = _PhotonDistributionResult

    def parse(self, group):
        data = {}
        for transition, group in group.items():
            transition = xraytransition.from_string(transition)

            for suffix, dataset in group.items():
                data.setdefault(transition, {})[suffix] = np.copy(dataset)

        # Construct distributions
        distributions = {}
        for transition, datum in data.items():
            distributions.update(create_photondist_dict(transition, **datum))

        return _PhotonDistributionResult(distributions)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)

        distributions = [('gnf', False, False), ('gt', False, True),
                         ('enf', True, False), ('et', True, True)]

        for suffix, absorption, fluorescence in distributions:
            for transition, data in obj.iter_transitions(absorption, fluorescence):
                name = '%s %s' % (transition.symbol, transition.iupac)
                subgroup = group.require_group(name)
                subgroup.create_dataset(suffix, data=data)

        return group

class PhotonDepthResultHDF5Handler(_PhotonDistributionResultHDF5Handler):

    CLASS = PhotonDepthResult

    def parse(self, group):
        dist = _PhotonDistributionResultHDF5Handler.parse(self, group)
        return PhotonDepthResult(dist._distributions)

class PhotonRadialResultHDF5Handler(_PhotonDistributionResultHDF5Handler):

    CLASS = PhotonRadialResult

    def parse(self, group):
        dist = _PhotonDistributionResultHDF5Handler.parse(self, group)
        return PhotonRadialResult(dist._distributions)

class TimeResultHDF5Handler(_HDF5Handler):

    CLASS = TimeResult

    def parse(self, group):
        simulation_time_s = group.attrs['simulation_time_s']
        simulation_speed_s = group.attrs['simulation_speed_s']
        return TimeResult(simulation_time_s, simulation_speed_s)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)
        group.attrs['simulation_time_s'] = obj.simulation_time_s
        group.attrs['simulation_speed_s'] = obj.simulation_speed_s
        return group

class ShowersStatisticsResultHDF5Handler(_HDF5Handler):

    CLASS = ShowersStatisticsResult

    def parse(self, group):
        showers = group.attrs['showers']
        return ShowersStatisticsResult(showers)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)
        group.attrs['showers'] = obj.showers
        return group

class ElectronFractionResultHDF5Handler(_HDF5Handler):

    CLASS = ElectronFractionResult

    def parse(self, group):
        absorbed = group.attrs['absorbed']
        backscattered = group.attrs['backscattered']
        transmitted = group.attrs['transmitted']
        return ElectronFractionResult(absorbed, backscattered, transmitted)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)
        group.attrs['absorbed'] = obj.absorbed
        group.attrs['backscattered'] = obj.backscattered
        group.attrs['transmitted'] = obj.transmitted
        return group

class TrajectoryResultHDF5Handler(_HDF5Handler):

    CLASS = TrajectoryResult

    def parse(self, group):
        particles_ref = list(PARTICLES)
        particles_ref = dict(zip(map(int, particles_ref), particles_ref))

        collisions_ref = list(COLLISIONS)
        collisions_ref = dict(zip(map(int, collisions_ref), collisions_ref))

        trajectories = []

        for dataset in group.values():
            primary = bool(dataset.attrs['primary'])
            particle = particles_ref[dataset.attrs['particle']]
            collision = collisions_ref[dataset.attrs['collision']]
            exit_state = int(dataset.attrs['exit_state'])
            interactions = dataset[:]

            trajectory = Trajectory(primary, particle, collision,
                                    exit_state, interactions)
            trajectories.append(trajectory)

        return TrajectoryResult(trajectories)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)

        for index, trajectory in enumerate(obj._trajectories):
            name = 'trajectory%s' % index
            dataset = group.create_dataset(name, data=trajectory.interactions)

            dataset.attrs['primary'] = trajectory.is_primary()
            dataset.attrs['particle'] = int(trajectory.particle)
            dataset.attrs['collision'] = int(trajectory.collision)
            dataset.attrs['exit_state'] = trajectory.exit_state

        return group

class _ChannelsResultHDF5Handler(_HDF5Handler):

    CLASS = _ChannelsResult

    def parse(self, group):
        data = np.copy(group['data'])
        return _ChannelsResult(data)

    def convert(self, obj, group):
        group = _HDF5Handler.convert(self, obj, group)
        group.create_dataset('data', data=obj.get_data())
        return group

class BackscatteredElectronEnergyResultHDF5Handler(_ChannelsResultHDF5Handler):

    CLASS = BackscatteredElectronEnergyResult

    def parse(self, group):
        result = _ChannelsResultHDF5Handler.parse(self, group)
        return BackscatteredElectronEnergyResult(result.get_data())

class TransmittedElectronEnergyResultHDF5Handler(_ChannelsResultHDF5Handler):

    CLASS = TransmittedElectronEnergyResult

    def parse(self, group):
        result = _ChannelsResultHDF5Handler.parse(self, group)
        return TransmittedElectronEnergyResult(result.get_data())

class BackscatteredElectronPolarAngularResultHDF5Handler(_ChannelsResultHDF5Handler):

    CLASS = BackscatteredElectronPolarAngularResult

    def parse(self, group):
        result = _ChannelsResultHDF5Handler.parse(self, group)
        return BackscatteredElectronPolarAngularResult(result.get_data())

class BackscatteredElectronRadialResultHDF5Handler(_ChannelsResultHDF5Handler):

    CLASS = BackscatteredElectronRadialResult

    def parse(self, group):
        result = _ChannelsResultHDF5Handler.parse(self, group)
        return BackscatteredElectronRadialResult(result.get_data())

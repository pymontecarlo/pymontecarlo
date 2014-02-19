#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Casino 2 results importer
================================================================================

.. module:: importer
   :synopsis: Casino 2 results importer

.. inheritance-diagram:: pymontecarlo.program.casino2.output.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.
import numpy as np

from pyxray.transition import K_family, LIII, MV

# Local modules.
from pymontecarlo.program.importer import Importer as _Importer
from pymontecarlo.results.result import \
    (
    PhotonIntensityResult,
    ElectronFractionResult,
    create_intensity_dict,
    PhotonDepthResult,
    PhotonRadialResult,
    create_photondist_dict,
    BackscatteredElectronEnergyResult,
    TransmittedElectronEnergyResult,
    BackscatteredElectronPolarAngularResult,
    BackscatteredElectronRadialResult,
    TrajectoryResult,
    Trajectory,
    )
from pymontecarlo.options.detector import \
    (
     BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonDepthDetector,
     PhotonRadialDetector,
     PhotonIntensityDetector,
     ElectronFractionDetector,
     TransmittedElectronEnergyDetector,
     TrajectoryDetector,
     )

from casinotools.fileformat.casino2.File import File

# Globals and constants variables.
from casinotools.fileformat.casino2.Element import \
    LINE_K, LINE_L, LINE_M, GENERATED as CAS_GENERATED, EMITTED as CAS_EMITTED
from pymontecarlo.results.result import \
    (GENERATED, EMITTED, NOFLUORESCENCE, TOTAL,
     EXIT_STATE_ABSORBED, EXIT_STATE_BACKSCATTERED, EXIT_STATE_TRANSMITTED)
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.collision import NO_COLLISION

LINE_LOOKUP = {LINE_K: K_family, LINE_L: LIII, LINE_M: MV}

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._importers[PhotonIntensityDetector] = self._import_photon_intensity
        self._importers[PhotonDepthDetector] = self._import_photon_depth
        self._importers[PhotonRadialDetector] = self._import_photon_radial
        self._importers[ElectronFractionDetector] = self._import_electron_fraction
        self._importers[BackscatteredElectronEnergyDetector] = \
            self._import_backscattered_electron_energy
        self._importers[TransmittedElectronEnergyDetector] = \
            self._import_transmitted_electron_energy
        self._importers[BackscatteredElectronPolarAngularDetector] = \
            self._import_backscattered_electron_polar_angular
        self._importers[BackscatteredElectronRadialDetector] = \
            self._import_backscattered_electron_radial
        self._importers[TrajectoryDetector] = self._import_trajectory

    def _import(self, options, dirpath, *args, **kwargs):
        filepath = os.path.join(dirpath, options.name + '.cas')

        with open(filepath, 'rb') as fileobj:
            return self.import_from_cas(options, fileobj)

    def import_cas(self, options, fileobj):
        # Read cas
        casfile = File()
        casfile.readFromFileObject(fileobj)

        simdata = casfile.getResultsFirstSimulation()

        return self._run_importers(options, simdata)

    def _import_photon_intensity(self, options, name, detector, simdata):
        cas_intensities = simdata.getTotalXrayIntensities()
        factor = detector.solidangle_sr / (0.0025 * 1e9)
        if factor == 0.0: factor = 1.0

        intensities = {}
        for z in cas_intensities:
            for line in cas_intensities[z]:
                transition = LINE_LOOKUP[line](z)
                datum = cas_intensities[z][line]

                gt = (datum[CAS_GENERATED] * factor, 0.0)
                et = (datum[CAS_EMITTED] * factor, 0.0)

                tmpints = create_intensity_dict(transition,
                                                gnf=gt, gt=gt,
                                                enf=et, et=et)
                intensities.update(tmpints)

        return PhotonIntensityResult(intensities)

    def _import_photon_depth(self, options, name, detector, simdata):
        simops = simdata.getSimulationOptions()
        dz = simops.EpaisCouche * 1e-9 # nm
        nz = simops.NbreCoucheRX
        zs = np.linspace(-nz * dz, 0.0, nz - 1, True)

        dists = {}

        for region in simdata.getRegionOptions().getRegions():
            for element in region.getElements():
                z = element.getAtomicNumber()
                delta = element.getDepthXrayDistribution()

                for line in delta.keys():
                    transition = LINE_LOOKUP[line](z)

                    delta_gnf = delta[line][CAS_GENERATED][::-1]
                    delta_enf = delta[line][CAS_EMITTED][::-1]

                    if transition in dists:
                        gnf = dists[transition][GENERATED][NOFLUORESCENCE]
                        gnf[:, 1] += delta_gnf

                        gt = dists[transition][GENERATED][TOTAL]
                        gt[:, 1] += delta_gnf

                        enf = dists[transition][EMITTED][NOFLUORESCENCE]
                        enf[:, 1] += delta_enf
                        et = dists[transition][EMITTED][TOTAL]
                        et[:, 1] += delta_enf
                    else:
                        gnf = np.array([zs, delta_gnf]).transpose()
                        enf = np.array([zs, delta_enf]).transpose()
                        dists.update(create_photondist_dict(transition,
                                                            gnf, gnf, enf, enf))

        return PhotonDepthResult(dists)

    def _import_photon_radial(self, options, name, detector, simdata):
        simops = simdata.getSimulationOptions()
        dr = simops.EpaisCouche * 1e-9 # nm
        nr = simops.NbreCoucheRX
        rs = np.linspace(0.0, dr * nr, nr, True)

        areas = np.pi * (rs[1:] ** 2 - rs[:-1] ** 2)
        rs = rs[:-1]

        dists = {}

        for region in simdata.getRegionOptions().getRegions():
            for element in region.getElements():
                z = element.getAtomicNumber()
                delta = element.getRadialXrayDistribution()

                for line in delta.keys():
                    transition = LINE_LOOKUP[line](z)

                    delta_gnf = delta[line][CAS_GENERATED] / areas
                    delta_enf = delta[line][CAS_EMITTED] / areas

                    if transition in dists:
                        gnf = dists[transition][GENERATED][NOFLUORESCENCE]
                        gnf[:, 1] += delta_gnf

                        gt = dists[transition][GENERATED][TOTAL]
                        gt[:, 1] += delta_gnf

                        enf = dists[transition][EMITTED][NOFLUORESCENCE]
                        enf[:, 1] += delta_enf
                        et = dists[transition][EMITTED][TOTAL]
                        et[:, 1] += delta_enf
                    else:
                        gnf = np.array([rs, delta_gnf]).transpose()
                        enf = np.array([rs, delta_enf]).transpose()
                        dists.update(create_photondist_dict(transition,
                                                            gnf, gnf, enf, enf))

        return PhotonRadialResult(dists)

    def _import_electron_fraction(self, options, name, detector, simdata):
        bse_intensity = simdata.getSimulationResults().BE_Intensity[0]
        return ElectronFractionResult(backscattered=(bse_intensity, 0.0))

    def _import_backscattered_electron_energy(self, options, name, detector, simdata):
        graphdata = simdata.getSimulationResults().getBackscatteredEnergyDistribution()

        data = np.array([graphdata.getPositions(), graphdata.getValues()]).T
        data[:, 0] *= 1000.0 # keV to eV

        return BackscatteredElectronEnergyResult(data)

    def _import_transmitted_electron_energy(self, options, name, detector, simdata):
        graphdata = simdata.getSimulationResults().getTransmittedEnergyDistribution()

        data = np.array([graphdata.getPositions(), graphdata.getValues()]).T
        data[:, 0] *= 1000.0 # keV to eV

        return TransmittedElectronEnergyResult(data)

    def _import_backscattered_electron_polar_angular(self, options, name, detector, simdata):
        graphdata = simdata.getSimulationResults().getBackscatteredAngleDistribution()

        data = np.array([graphdata.getPositions(), graphdata.getValues()]).T
        data[:, 0] = np.deg2rad(data[:, 0]) # deg to rad

        return BackscatteredElectronPolarAngularResult(data)

    def _import_backscattered_electron_radial(self, options, name, detector, simdata):
        graphdata = simdata.getSimulationResults().getSurfaceRadiusBseDistribution()

        data = np.array([graphdata.getPositions(), graphdata.getValues()]).T
        data[:, 0] *= 1e-9 # nm to m
        data[:, 1] *= 1e9 ** 2 # nm2 to m2

        return BackscatteredElectronRadialResult(data)

    def _import_trajectory(self, options, name, detector, simdata):
        trajdata = simdata.getTrajectoriesData()
        trajectories = []

        for castrajectory in trajdata.getTrajectories():
            events = castrajectory.getScatteringEvents()
            interactions = np.empty((len(events), 6), dtype='float')

            for i, event in enumerate(events):
                x = event.X * 1e-9
                y = event.Y * 1e-9
                z = -event.Z * 1e-9
                e = event.E * 1e3
                interactions[i] = [x, y, z, e, -1, event.id]

            if castrajectory.isBackscattered():
                exit_state = EXIT_STATE_BACKSCATTERED
            elif castrajectory.isTransmitted():
                exit_state = EXIT_STATE_TRANSMITTED
            else:
                exit_state = EXIT_STATE_ABSORBED

            trajectory = Trajectory(True, ELECTRON, NO_COLLISION, exit_state, interactions)
            trajectories.append(trajectory)

        return TrajectoryResult(trajectories)

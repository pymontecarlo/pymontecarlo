#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- PENEPMA importer
================================================================================

.. module:: importer
   :synopsis: PENEPMA importer

.. inheritance-diagram:: pymontecarlo.program.penepma.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.results.result import TrajectoryResult, Trajectory
from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.options.collision import \
    (NO_COLLISION, DELTA, SOFT_EVENT, HARD_ELASTIC, HARD_INELASTIC,
     HARD_BREMSSTRAHLUNG_EMISSION, INNERSHELL_IMPACT_IONISATION,
     COHERENT_RAYLEIGH_SCATTERING, INCOHERENT_COMPTON_SCATTERING,
     PHOTOELECTRIC_ABSORPTION, ELECTRON_POSITRON_PAIR_PRODUCTION, ANNIHILATION)
from pymontecarlo.options.detector import TrajectoryDetector

from pymontecarlo.program.importer import Importer as _Importer, ImporterException

# Globals and constants variables.
_PARTICLES_REF = {1: ELECTRON, 2: PHOTON, 3: POSITRON}
_COLLISIONS_REF = {ELECTRON: {1: SOFT_EVENT,
                              2: HARD_ELASTIC,
                              3: HARD_INELASTIC,
                              4: HARD_BREMSSTRAHLUNG_EMISSION,
                              5: INNERSHELL_IMPACT_IONISATION,
                              7: DELTA},
                   PHOTON: {1: COHERENT_RAYLEIGH_SCATTERING,
                            2: INCOHERENT_COMPTON_SCATTERING,
                            3: PHOTOELECTRIC_ABSORPTION,
                            4: ELECTRON_POSITRON_PAIR_PRODUCTION,
                            7: DELTA},
                   POSITRON: {1: SOFT_EVENT,
                              2: HARD_ELASTIC,
                              3: HARD_INELASTIC,
                              4: HARD_BREMSSTRAHLUNG_EMISSION,
                              5: INNERSHELL_IMPACT_IONISATION,
                              6: ANNIHILATION,
                              7: DELTA}}

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._importers[TrajectoryDetector] = self._import_trajectory

    def _import(self, options, dirpath, *args, **kwargs):
        return self._run_importers(options, dirpath, *args, **kwargs)

    def _import_trajectory(self, options, key, detector, dirpath, *args, **kwargs):
        filepath = os.path.join(dirpath, 'pe-trajectories.dat')
        if not os.path.exists(filepath):
            raise ImporterException("Data file %s cannot be found" % filepath)

        trajectories = {}

        index = 0
        primary = None
        particle = None
        collision = None
        exit_state = None
        interactions = []

        with open(filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if line == '0' * 80:
                    if index <= 0:
                        continue

                    traj = Trajectory(primary, particle, collision, exit_state,
                                      np.array(interactions))
                    trajectories[index] = traj

                    primary = None
                    particle = None
                    collision = None
                    exit_state = None
                    interactions = []
                elif line == '1' * 80:
                    continue
                elif line.startswith('TRAJ'):
                    index = int(line.split()[1])
                elif line.startswith('KPAR'):
                    particle = _PARTICLES_REF[int(line.split()[1])]
                elif line.startswith('PARENT'):
                    primary = int(line.split()[1]) == 0
                elif line.startswith('ICOL'):
                    collision = _COLLISIONS_REF[particle].get(int(line.split()[1]), NO_COLLISION)
                elif line.startswith('EXIT'):
                    exit_state = int(line.split()[1])
                else:
                    values = line.split()
                    x = float(values[0]) * 0.01 # cm to m
                    y = float(values[1]) * 0.01 # cm to m
                    z = float(values[2]) * 0.01 # cm to m
                    e = float(values[3])
                    c = int(_COLLISIONS_REF[particle].get(int(values[6]), NO_COLLISION))
                    interactions.append([x, y, z, e, c])

        return TrajectoryResult(trajectories.values())

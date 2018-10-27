"""
Trajectory results.
"""

# Standard library modules.
import collections

# Third party modules.

# Local modules.
from pymontecarlo.results.base import Result, ResultBuilder

# Globals and constants variables.

class Trajectory:

    def __init__(self, particle, exited, xs_m, ys_m, zs_m, energies_eV, parent=None):
        if len(ys_m) != len(xs_m):
            raise ValueError('Number of y-coordinates ({}) is different than number of x-coordinates ({})' \
                             .format(len(ys_m), len(xs_m)))
        if len(zs_m) != len(xs_m):
            raise ValueError('Number of z-coordinates ({}) is different than number of x-coordinates ({})' \
                             .format(len(zs_m), len(xs_m)))
        if len(energies_eV) != len(xs_m):
            raise ValueError('Number of energies ({}) is different than number of x-coordinates ({})' \
                             .format(len(energies_eV), len(xs_m)))

        self.particle = particle
        self.exited = exited
        self.xs_m = tuple(xs_m)
        self.ys_m = tuple(ys_m)
        self.zs_m = tuple(zs_m)
        self.energies_eV = tuple(energies_eV)
        self.parent = parent

class TrajectoryResult(Result, collections.Iterable, collections.Sized):
    """
    Trajectory results.
    It consists of an iterable class containing :class:`Trajectory` objects.
    """

    def __init__(self, analysis, trajectories):
        super().__init__(analysis)
        self.trajectories = tuple(trajectories)

    def __len__(self):
        return len(self.trajectories)

    def __iter__(self):
        return iter(self.trajectories)

    def __repr__(self):
        return '<{}({} trajectories)>'.format(self.__class__.__name__, len(self))

class TrajectoryResultBuilder(ResultBuilder):

    def __init__(self, analysis):
        super().__init__(analysis)
        self.trajectories = []

    def add(self, trajectory):
        self.trajectories.append(trajectory)

    def build(self):
        return TrajectoryResult(self.analysis, self.trajectories)

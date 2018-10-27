"""
Trajectory results.
"""

# Standard library modules.
import collections
import dataclasses
import typing

# Third party modules.

# Local modules.
from pymontecarlo.results.base import Result, ResultBuilder
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

@dataclasses.dataclass
class Trajectory:
    id: int
    parent_id: int
    particle: Particle
    exited: bool
    xs_m: typing.List[float]
    ys_m: typing.List[float]
    zs_m: typing.List[float]
    energies_eV: typing.List[float]
    events: typing.List[int]

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
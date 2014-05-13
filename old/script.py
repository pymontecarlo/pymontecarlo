from math import radians
import time
import logging

logging.getLogger().setLevel(logging.DEBUG)

from pyxray.transition import Ka

from optimization.optimizer import LevenbergMarquardtOptimzier
from pymontecarlo.runner.local import LocalRunner
from pymontecarlo.program.nistmonte.config import program as NISTMonte

from pymontecarlo.reconstruction.experiment import Experiment
from pymontecarlo.reconstruction.measurement import Measurement
from pymontecarlo.reconstruction.parameter import Parameter
from pymontecarlo.reconstruction.reconstructor import Reconstructor

from pymontecarlo.input import Inclusion, pure, Material, Options, ShowersLimit, PhotonIntensityDetector, composition_from_formula

baseops = Options()
baseops.beam.energy_eV = 10e3
baseops.beam.diameter_m = 50e-9
baseops.detectors['xray'] = PhotonIntensityDetector.annular(radians(40.0), radians(5.0))
baseops.limits.add(ShowersLimit(1000))

meas1 = Measurement(baseops)
meas1.add_kratio(Ka(6), 0.5, standard=Material('Fe3C', composition_from_formula('Fe3C')))

def setter1(geometry, val):
    geometry.inclusion_material.composition = {26: val, 6: '?'}
param1 = Parameter(setter1, 0.95, 0.0, 1.0)

def setter2(geometry, val):
    geometry.inclusion_diameter_m = val
param2 = Parameter(setter2, 200e-9, 150e-9, 250e-9)

inclusion_material = Material('CrC', {26: 0.95, 6: 0.05})
geometry = Inclusion(pure(26), inclusion_material, 200e-9)
exp = Experiment(geometry, [meas1], [param1, param2])

runner = LocalRunner(NISTMonte, '/tmp', nbprocesses=1)

optimizer = LevenbergMarquardtOptimzier()
reconstructor = Reconstructor(runner, optimizer, exp)
print reconstructor.reconstruct()



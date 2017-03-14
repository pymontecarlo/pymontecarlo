import math

# Create options
import pymontecarlo
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import HorizontalLayerSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analyses import KRatioAnalysis
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.options import Options

program = pymontecarlo.settings.get_program('casino2')

beam = GaussianBeam(15e3, 10e-9)

mat1 = Material.pure(29)
mat2 = Material.from_formula('Al2O3')
mat3 = Material('Stuff', {27: 0.5, 25: 0.2, 8: 0.3}, 4500.0)

sample = HorizontalLayerSample(mat1)
sample.add_layer(mat2, 10e-9)
sample.add_layer(mat3, 25e-9)

photon_detector = PhotonDetector(math.radians(35.0))
analysis = KRatioAnalysis(photon_detector)

limit = ShowersLimit(1000)

options = Options(program, beam, sample, [analysis], [limit])

# Run simulation
from pymontecarlo.runner.local import LocalSimulationRunner
from pymontecarlo.project import Project

project = Project()

with LocalSimulationRunner(project) as runner:
    future = runner.submit(options)

    while not runner.wait(1):
        print(runner.progress, future.progress)

    print(future.result())

# Results
project.recalculate()
print('{} were simulated'.format(len(project.simulations)))


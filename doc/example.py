import math

# Create options
import pymontecarlo
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import HorizontalLayerSample, SubstrateSample, VerticalLayerSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import KRatioAnalysis
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.options import Options

program = pymontecarlo.settings.get_program('casino2')

beam = GaussianBeam(15e3, 10e-9)

mat1 = Material.pure(29)
mat2 = Material.from_formula('SiO2')
mat3 = Material('Stuff', {27: 0.5, 25: 0.2, 8: 0.3}, 4500.0)

sample = SubstrateSample(mat2)

#sample = HorizontalLayerSample(mat3)
#sample.add_layer(mat2, 10e-9)
#sample.add_layer(mat3, 25e-9)

#sample = VerticalLayerSample(mat1, mat2)
#sample.add_layer(mat3, 10e-9)

photon_detector = PhotonDetector(math.radians(35.0))
analysis = KRatioAnalysis(photon_detector)

limit = ShowersLimit(1000)

options = Options(program, beam, sample, [analysis], [limit])

# Run simulation
from pymontecarlo.runner.local import LocalSimulationRunner
from pymontecarlo.project import Project

project = Project()

with LocalSimulationRunner(project, max_workers=3) as runner:
    futures = runner.submit(options)
    print('{} simulations launched'.format(len(futures)))

    while not runner.wait(1):
        print(runner.progress)

    print('{} simulations succeeded'.format(runner.done_count))
    print('{} simulations failed'.format(runner.failed_count))
    for future in runner.failed_futures:
        print(future.exception())

# Results
project.recalculate()
print('{} were simulated'.format(len(project.simulations)))
for simulation in project.simulations:
    print(simulation.results)

project.write('/tmp/example.mcsim')
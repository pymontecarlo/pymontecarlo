import os
import time
from math import radians

# Options
from pymontecarlo.input import *

ops = Options('simulation1')
ops.beam.energy_eV = 5e3

ops.geometry = MultiLayers(Material('Brass', {30: 0.37, 29: '?'}))
ops.geometry.add_layer(pure(28), 500e-9) # 500 nm thick

elevation=(radians(35), radians(45)) # Take-off angle: 40 deg
azimuth=(0.0, radians(360)) # Annular detector
ops.detectors['intensity'] = PhotonIntensityDetector(elevation, azimuth)
ops.detectors['spectrum'] = \
    PhotonSpectrumDetector(elevation, azimuth, (0.0, ops.beam.energy_eV), 1000)

ops.limits.add(ShowersLimit(10000))
ops.models.add(ELASTIC_CROSS_SECTION.rutherford)

# Converter, Exporter, Importer -> Worker
from pymontecarlo.runner.runner import Runner
from pymontecarlo.program.nistmonte.runner.worker import Worker # Program specific

outputdir = '/tmp' # TO BE CHANGED
runner = Runner(Worker, outputdir, nbprocesses=1)
runner.put(ops)

runner.start()

while runner.is_alive():
    counter, progress, status = runner.report()
    print counter, progress, status
    time.sleep(1)

runner.stop() # Not really required, but to be saved

# Results
from pymontecarlo.output.results import Results

results = Results.load(os.path.join(outputdir, ops.name + '.h5'))

print results['intensity'].intensity('Ni La')


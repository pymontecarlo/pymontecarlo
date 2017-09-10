from math import radians
import time
from pymontecarlo.input import *

# Setup simulation options
ops = Options("example")

ops.beam.energy_keV = 20.0

mat = Material("Cementite", composition_from_formula('Fe3C'))
ops.geometry = Substrate(mat)

toa_rad = radians(40.0)
opening_rad = radians(5.0)
ops.detectors['xrays'] = PhotonIntensityDetector.annular(toa_rad, opening_rad)

ops.limits.add(ShowersLimit(10))

# Select simulation program
# Could be change to other program
from pymontecarlo.program.nistmonte.config import program

# Run simulation
from pymontecarlo.runner.local import LocalRunner

outputdir = "/tmp"
with LocalRunner(program, outputdir) as runner:
    runner.put(ops)

    while runner.is_alive():
        _completed, progress, status = runner.report()
        print '%4.2f %% %s' % (progress * 100.0, status)
        time.sleep(5.0)

    list_results = runner.get_results()

# Extract carbon Ka intensity
results = list_results[0] # Only one simulation
results.save('/tmp/results.h5')
intensity, intensity_unc = results[0]['xrays'].intensity("C Ka")
print intensity, 'counts / (sr.electron)'

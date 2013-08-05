from math import radians
import time
from operator import itemgetter
from pymontecarlo.input import *

# Setup simulation options
ops = Options("linescan")

ops.beam.energy_keV = 20.0

origins = []
for x in range(-500, 501, 100):
    origins.append((x, 0, 1e3))
ops.beam.origin_nm = origins

mat_left = pure(26)
mat_right = pure(28)
ops.geometry = GrainBoundaries(mat_left, mat_right)

toa_rad = radians(40.0)
opening_rad = radians(5.0)
ops.detectors['xrays'] = PhotonIntensityDetector.annular(toa_rad, opening_rad)

ops.limits.add(ShowersLimit(10000))

ops.models.add(FLUORESCENCE.fluorescence_compton)

# Select simulation program
# Could be change to other program
from pymontecarlo.program.nistmonte.config import program

# Run simulation
from pymontecarlo.runner.local import LocalRunner

outputdir = "/tmp"
with LocalRunner(program, outputdir, nbprocesses=2) as runner:
    runner.put(ops)

    while runner.is_alive():
        completed, progress, status = runner.report()
        print '%i completed, %4.2f %% %s' % (completed, progress * 100.0, status)
        time.sleep(5.0)

    list_results = runner.get_results()

# Extract intensities
data = []
for results in list_results[0]:
    x = results.options.beam.origin_nm[0]
    int_fe, _unc = results['xrays'].intensity('Fe Ka')
    int_ni, _unc = results['xrays'].intensity('Ni Ka')
    data.append((x, int_fe, int_ni))

data.sort(key=itemgetter(0)) # Sort by position

xs = map(itemgetter(0), data)
intensities_fe = map(itemgetter(1), data)
intensities_ni = map(itemgetter(2), data)

# Graph (optional)
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot("111")

ax.plot(xs, intensities_fe, label=r'Fe K$\alpha$')
ax.plot(xs, intensities_ni, label=r'Ni K$\alpha$')

ax.set_xlabel('Distance (nm)')
ax.set_ylabel('Intensity (counts / (sr.electron))')

ax.legend()

plt.show()

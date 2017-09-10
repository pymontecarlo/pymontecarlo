#!/usr/bin/env python3
""""""

# Standard library modules.
import math, sys
import matplotlib.pyplot as plt

# Third party modules.

# Local modules
# Create options
import pymontecarlo
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import HorizontalLayerSample, SubstrateSample, VerticalLayerSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analyses import KRatioAnalysis
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.options import Options

from pymontecarlo.options.beam.base import Beam, BeamBuilder
from pymontecarlo.options.beam.gaussian import GaussianBeamBuilder
from pymontecarlo.options.base import Option, OptionBuilder

from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder, \
    EmittedPhotonIntensityResult
from pymontecarlo.options.analyses.photon import PhotonAnalysis
from pymontecarlo.options.analyses.photonintensity import PhotonIntensityAnalysis


def main(argv=None):
    program = pymontecarlo.settings.get_program('casino2')

    # beam = GaussianBeam(15e3, 10e-9)

    mat1 = Material.pure(26)
    mat2 = Material.pure(14)
    # mat2 = Material.from_formula('SiO2')
    # mat3 = Material('Stuff', {27: 0.5, 25: 0.2, 8: 0.3}, 4500.0)

    # sample = SubstrateSample(mat2)

    # sample = HorizontalLayerSample(mat3)
    # sample.add_layer(mat2, 10e-9)
    # sample.add_layer(mat3, 25e-9)

    sample = VerticalLayerSample(mat1, mat2)
    # sample.add_layer(mat3, 10e-9)

    photon_detector = PhotonDetector(math.radians(35.0))
    # analysis = KRatioAnalysis(photon_detector)
    analysis = PhotonIntensityAnalysis(photon_detector)

    limit = ShowersLimit(1000)

    b = GaussianBeamBuilder()
    b.add_energy_eV(15e3)
    b.add_diameter_m(10e-9)
    b.add_linescan_x(-1e-07, 1e-07, 5e-08)

    beams = b.build()

    print('beams', beams)

    opt = []

    for beam in beams:
        opt.append(Options(program, beam, sample, [analysis], [limit]))

    # Run simulation
    from pymontecarlo.runner.local import LocalSimulationRunner
    from pymontecarlo.project import Project

    project = Project()

    # for options in opt:

    with LocalSimulationRunner(project, max_workers=3) as runner:

        futures = [runner.submit(o) for o in opt]

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

    ################################################################################################
    ###                           Ab hier wird es relevant                                       ###
    ################################################################################################

    # Hier werden die Ergebnisse gespeichert
    data_all = []

    for simulation in project.simulations:
        # results = simulation.results
        position = simulation.options.beam.x0_m

        for unkresult in simulation.find_result(EmittedPhotonIntensityResult):

            for xrayline, unkintensity in unkresult.items():
                # z = xrayline.atomic_number
                data = unkintensity.nominal_value
                data_all.append((xrayline, position, data))

    results = {}

    # Zu jeder simulierten Röntgenlinie wird der Datensatz in einem Dictionary gespeichert
    for x, p, d in data_all:
        if not x in results:
            results[x] = []
        results[x].append((p, d))

    # Sortiere Werte und gebe sie aus
    sorted_results = []
    for k, v in results.items():
        v.sort(key=lambda t: t[0])
        print('{}\t{}'.format(k, v))
        print(v)
        plot_results(k, v)
        sorted_results.append(k,v)
        
    return sorted_results
    print(sorted_results)

def plot_results(label, listoftuples):
    #ylabels = {'kratio': 'k-ratio', 'mass': 'Mass (%)', 'atom': 'Atom (%)'}
    
    fig = plt.figure()
    ax = fig.add_subplot("111")
    
    ax.set_xlabel('Distance (nm)')
    ax.set_ylabel('Intensity')
    plt.plot((*zip(*listoftuples)), label = label)
    plt.legend()
    plt.show()
    print(label)

if __name__ == '__main__':
    sys.exit(main(sys.argv))

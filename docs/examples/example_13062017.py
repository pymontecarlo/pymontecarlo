#!/usr/bin/env python3
""""""

# Standard library modules.
import math, sys
import matplotlib.pyplot as plt

# Third party modules.

# Local modules
# Create options
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import (
    HorizontalLayerSample,
    SubstrateSample,
    VerticalLayerSample,
)
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import KRatioAnalysis, PhotonIntensityAnalysis
from pymontecarlo.options.options import OptionsBuilder

from pymontecarlo.options.beam.gaussian import GaussianBeamBuilder

from pymontecarlo.results.photonintensity import (
    EmittedPhotonIntensityResultBuilder,
    EmittedPhotonIntensityResult,
)

from pymontecarlo.runner.local import LocalSimulationRunner
from pymontecarlo.project import Project

from pymontecarlo_casino2.program import Casino2Program


def main(argv=None):
    options_builder = OptionsBuilder()

    program = Casino2Program()
    program.number_trajectories = 1000
    options_builder.add_program(program)

    beam_builder = GaussianBeamBuilder()
    beam_builder.add_energy_eV(15e3)
    beam_builder.add_diameter_m(10e-9)
    beam_builder.add_linescan_x(-1e-07, 1e-07, 5e-08)
    beams = beam_builder.build()
    print("beams", beams)
    options_builder.beams.extend(beams)

    mat1 = Material.pure(26)
    mat2 = Material.pure(14)
    sample = VerticalLayerSample(mat1, mat2)
    options_builder.add_sample(sample)

    photon_detector = PhotonDetector("xray", math.radians(35.0))
    # analysis = KRatioAnalysis(photon_detector)
    analysis = PhotonIntensityAnalysis(photon_detector)
    options_builder.add_analysis(analysis)

    list_options = options_builder.build()

    # Run simulation
    project = Project()

    # for options in opt:

    with LocalSimulationRunner(project, max_workers=3) as runner:
        futures = runner.submit(*list_options)

        print("{} simulations launched".format(len(futures)))

        while not runner.wait(1):
            print(runner.progress)

            print("{} simulations succeeded".format(runner.done_count))
            print("{} simulations failed".format(runner.failed_count))
            for future in runner.failed_futures:
                print(future.exception())

    # Results
    project.recalculate()
    print("{} were simulated".format(len(project.simulations)))

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
        print("{}\t{}".format(k, v))
        print(v)
        plot_results(k, v)
        sorted_results.append((k, v))

    return sorted_results
    print(sorted_results)


def plot_results(label, listoftuples):
    # ylabels = {'kratio': 'k-ratio', 'mass': 'Mass (%)', 'atom': 'Atom (%)'}

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel("Distance (nm)")
    ax.set_ylabel("Intensity")
    plt.plot(*zip(*listoftuples), label=label)
    plt.legend()
    plt.show()
    print(label)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

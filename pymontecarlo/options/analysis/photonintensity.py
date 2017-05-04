"""
Analysis to record photon intensity emitted towards a detector.
"""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.analysis.photon import \
    PhotonAnalysis, PhotonAnalysisBuilder, COMMON_XRAY_TRANSITION_SETS
from pymontecarlo.results.photonintensity import PhotonIntensityResult
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class PhotonIntensityAnalysis(PhotonAnalysis):

    def __init__(self, photon_detector):
        super().__init__(photon_detector)

    def apply(self, options):
        return []

    def calculate(self, simulation, simulations):
        """
        Calculate additional photon intensities for common X-ray transition sets.
        """
        newresult = super().calculate(simulation, simulations)

        for result in simulation.find_result(PhotonIntensityResult):
            zs = set(xrayline.atomic_number for xrayline in result)

            for z in zs:
                possible_transitions = set(pyxray.element_xray_transitions(z))

                for transitionset in COMMON_XRAY_TRANSITION_SETS:
                    # Check if it already exists
                    xrayline = XrayLine(z, transitionset)
                    if xrayline in result:
                        continue

                    # Only add possible transitions for this element
                    transitions = possible_transitions & transitionset.transitions
                    if not transitions:
                        continue

                    subxraylines = []
                    total = 0.0
                    for transition in transitions:
                        subxrayline = XrayLine(z, transition)
                        q = result.get(subxrayline, None)
                        if q is None:
                            break

                        subxraylines.append(subxrayline)
                        total += q

                    if len(subxraylines) != len(transitions):
                        continue

                    result.data[xrayline] = total
                    newresult = True

        return newresult

class PhotonIntensityAnalysisBuilder(PhotonAnalysisBuilder):

    def build(self):
        return [PhotonIntensityAnalysis(d) for d in self.photon_detectors]

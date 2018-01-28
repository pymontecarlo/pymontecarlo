"""
Analysis to record photon intensity emitted towards a detector.
"""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.analysis.photon import \
    PhotonAnalysisBase, PhotonAnalysisBuilderBase, COMMON_XRAY_TRANSITION_SETS
from pymontecarlo.results.photonintensity import PhotonIntensityResultBase

# Globals and constants variables.

class PhotonIntensityAnalysis(PhotonAnalysisBase):

    def __init__(self, photon_detector):
        super().__init__(photon_detector)

    def apply(self, options):
        return []

    def calculate(self, simulation, simulations):
        """
        Calculate additional photon intensities for common X-ray transition sets.
        """
        newresult = super().calculate(simulation, simulations)

        for result in simulation.find_result(PhotonIntensityResultBase):
            zs = set(xrayline.element.atomic_number for xrayline in result)

            for z in zs:
                for transitionset in COMMON_XRAY_TRANSITION_SETS:
                    # Check if transition set exists for element
                    try:
                        xrayline = pyxray.xray_line(z, transitionset)
                    except pyxray.NotFound:
                        continue

                    # Check if it already exists
                    if xrayline in result:
                        continue

                    # Add counts
                    subxraylines = []
                    total = 0.0
                    for transition in xrayline.transitions:
                        subxrayline = pyxray.xray_line(z, transition)
                        q = result.get(subxrayline, None)
                        if q is None:
                            break

                        subxraylines.append(subxrayline)
                        total += q

                    # Check if all transitions were found
                    if len(subxraylines) != len(xrayline.transitions):
                        continue

                    # Add result
                    result.data[xrayline] = total
                    newresult = True

        return newresult

class PhotonIntensityAnalysisBuilder(PhotonAnalysisBuilderBase):

    def build(self):
        return [PhotonIntensityAnalysis(d) for d in self.photon_detectors]

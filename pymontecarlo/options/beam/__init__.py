"""
Incident beams.
"""

from pymontecarlo.options.beam.base import convert_diameter_fwhm_to_sigma, convert_diameter_sigma_to_fwhm
from pymontecarlo.options.beam.gaussian import GaussianBeam, GaussianBeamBuilder

"""
Bremsstrahlung emission models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class BremsstrahlungEmissionModel(Model):

    @property
    def category(self):
        return 'bremsstrahlung emission'

SELTZER_BERGER1985 = BremsstrahlungEmissionModel('Seltzer and Berger', 'Seltzer, S., & Berger, M. (1985). Bremsstrahlung spectra from electron interactions with screened atomic nuclei and orbital electrons. Nucl. Instrum. Meth. B, 12, 95-134.')

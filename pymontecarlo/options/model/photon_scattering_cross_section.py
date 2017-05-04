"""
Photon scattering cross section models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class PhotonScatteringCrossSectionModel(Model):

    BRUSA1996 = ('Brusa et al. photon compton scattering', 'Brusa, D., Stutz, G., Riveros, J., Fernandez-Vera, J., & Salvat, F. (1996). Fast sampling algorithm for the simulation of photon compton scattering. Nucl. Instrum. Meth. A, 379, 167-175.')

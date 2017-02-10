"""
Elastic cross section models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class ElasticCrossSectionModel(Model):

    @property
    def category(self):
        return 'elastic cross section'

MOTT_CZYZEWSKI1990 = \
    ElasticCrossSectionModel('Mott by interpolation (Czyzewski)', 'Czyzewski (1990)')
MOTT_CZYZEWSKI1990_LINEAR = \
    ElasticCrossSectionModel('Mott by linear interpolation (Czyzewski)', 'Czyzewski (1990)')
MOTT_CZYZEWSKI1990_POWERLAW = \
    ElasticCrossSectionModel('Mott by power law interpolation (Czyzewski)', 'Czyzewski (1990)')
MOTT_CZYZEWSKI1990_CUBICSPLINE = \
    ElasticCrossSectionModel('Mott by cubic spline interpolation (Czyzewski)', 'Czyzewski (1990)')
MOTT_DEMERS = \
    ElasticCrossSectionModel('Mott parametrized (Demers)', 'Demers')
MOTT_DROUIN1993 = \
    ElasticCrossSectionModel('Mott by equation (Drouin)', 'Drouin and Gauvin (1993)')
MOTT_BROWNING1994 = \
    ElasticCrossSectionModel('Mott by equation (Browning)', 'Browning (1994)')
RUTHERFORD = \
    ElasticCrossSectionModel('Rutherford')
RUTHERFORD_RELATIVISTIC = \
    ElasticCrossSectionModel('Rutherford relativistic')
ELSEPA2005 = \
    ElasticCrossSectionModel('ELSEPA', 'Salvat, F., Jablonski, A., & Powell, C. (2005). ELSEPA - Dirac partial-wave calculation of elastic scattering of electrons and positrons by atoms, positive ions and molecules. Comput. Phys. Commun., 165, 157-190.')
REIMER = \
    ElasticCrossSectionModel('Reimer')

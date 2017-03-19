"""
Elastic cross section models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class ElasticCrossSectionModel(Model):

    MOTT_CZYZEWSKI1990 = ('Mott by interpolation (Czyzewski)', 'Czyzewski (1990)')
    MOTT_CZYZEWSKI1990_LINEAR = ('Mott by linear interpolation (Czyzewski)', 'Czyzewski (1990)')
    MOTT_CZYZEWSKI1990_POWERLAW = ('Mott by power law interpolation (Czyzewski)', 'Czyzewski (1990)')
    MOTT_CZYZEWSKI1990_CUBICSPLINE = ('Mott by cubic spline interpolation (Czyzewski)', 'Czyzewski (1990)')
    MOTT_DEMERS = ('Mott parametrized (Demers)', 'Demers')
    MOTT_DROUIN1993 = ('Mott by equation (Drouin)', 'Drouin and Gauvin (1993)')
    MOTT_BROWNING1994 = ('Mott by equation (Browning)', 'Browning (1994)')
    RUTHERFORD = ('Rutherford')
    RUTHERFORD_RELATIVISTIC = ('Rutherford relativistic')
    ELSEPA2005 = ('ELSEPA', 'Salvat, F., Jablonski, A., & Powell, C. (2005). ELSEPA - Dirac partial-wave calculation of elastic scattering of electrons and positrons by atoms, positive ions and molecules. Comput. Phys. Commun., 165, 157-190.')
    REIMER = ('Reimer')

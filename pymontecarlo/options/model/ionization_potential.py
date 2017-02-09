"""
Ionization potential models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class IonizationPotentialModel(Model):

    NAME = 'ionization potential model'
    DESCRIPTION = 'Models inner-shell ionization of atoms.'

    @property
    def category(self):
        return 'ionization potential'

JOY_LUO1989 = IonizationPotentialModel('Joy and Luo', 'Joy and Luo (1989)')
BERGER_SELTZER1964 = IonizationPotentialModel("Berger & Seltzer 1964", "Berger MJ, Seltzer S. NASA Technical Publication SP-4012 (1964)")
BERGER_SELTZER1983 = IonizationPotentialModel("Berger & Seltzer 1983", "Berger MJ, Seltzer S. NBSIR 82-2550-A - US Dept of Commerce, Washington DC (1983)")
BERGER_SELTZER1983_CITZAF = IonizationPotentialModel("Berger & Seltzer 1983 (CITZAF)", "Berger and Seltzer as implemented by CITZAF 3.06")
ZELLER1975 = IonizationPotentialModel("Zeller 1975", "Zeller C in Ruste J, Gantois M, J. Phys. D. Appl. Phys 8, 872 (1975)")
DUNCUMB_DECASA1969 = IonizationPotentialModel("Duncumb & DeCasa 1969", "Duncumb P, Shields-Mason PK, DeCasa C. Proc. 5th Int. Congr. on X-ray Optics and Microanalysis, Springer, Berlin, 1969 p. 146")
HEINRICH_YAKOWITZ1970 = IonizationPotentialModel("Heinrich & Yakowitz 1970", "Heinrich KFJ, Yakowitz H. Mikrochim Acta (1970) p 123")
SPRINGER1967 = IonizationPotentialModel("Springer 1967", "Springer G. Meues Jahrbuch Fuer Mineralogie, Monatshefte (1967) 9/10, p. 304")
WILSON1941 = IonizationPotentialModel("Wilson 1941", "Wilson RR. Phys Rev. 60. 749 (1941)")
BLOCH1933 = IonizationPotentialModel("Bloch 1933", "Bloch F, F. Z. Phys. 81, 363 (1933)")
STERNHEIMER1964 = IonizationPotentialModel("Sternheimer 1964", "Sternheimer quoted in Berger MJ, Seltzer S. NASA Technical Publication SP-4012 (1964)")
HOVINGTON = IonizationPotentialModel('Hovington',)
GRYZINSKI = IonizationPotentialModel('Gryzinski',)

"""
Mass absorption coefficient models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class MassAbsorptionCoefficientModel(Model):

    NONE = ('No MAC')
    RUSTE1979 = ('Ruste 1979', 'J. Ruste, J. Microsc. Spectrosc. Electron. 4, 123 (1979)')
    POUCHOU_PICHOIR1991 = ('Pouchou and Pichoir 1991', 'Pouchou & Pichoir in Electron Probe Quantitation, Eds Heinrich and Newbury')
    POUCHOU_PICHOIR1988 = ('Pouchou and Pichoir 1988', "J. L. Pouchou and F. M. A. Pichoir, 'Determination of Mass Absorption Coefficients for Soft X-Rays by use of the Electron Microprobe' Microbeam Analysis, Ed. D. E. Newbury, San Francisco Press, 1988, p. 319-324")
    HENKE1982 = ('Henke 1982', "B. L. Henke, P. Lee, T. J. Tanaka, R. L. Shimabukuro and B. K. Fijikawa, Atomic Data Nucl. Data Tables 27, 1 (1982)")
    HENKE1993 = ('Henke 1993', "B.L. Henke, E.M. Gullikson and J.C. Davis (1993). X-ray interactions: photoabsorption, scattering, transmission, and reflection at E=50-30000 eV, Z=1-92, Atomic Data and Nuclear Data Tables, 54, pp. 181-342")
    BASTIN_HEIJLIGERS1989 = ('Bastin and Heijligers 1985 1988 1989', "as quoted in Scott, Love & Reed, Quantitative Electron-Probe Microanalysis, 2nd ed.")
    HEINRICH_IXCOM11_DTSA = ('Heinrich IXCOM 11 (DTSA)', "Heinrich KFJ. in Proc. 11th Int. Congr. X-ray Optics & Microanalysis, Brown JD, Packwood RH (eds). Univ. Western Ontario: London, 1986; 67")
    HEINRICH_IXCOM11 = ('Heinrich IXCOM 11', "Heinrich KFJ. in Proc. 11th Int. Congr. X-ray Optics & Microanalysis, Brown JD, Packwood RH (eds). Univ. Western Ontario: London, 1986; 67")
    CHANTLER2005 = ('NIST-Chantler 2005', "See http://physics.nist.gov/ffast")
    DTSA_CITZAF = ('DTSA CitZAF', "DTSA at http://www.cstl.nist.gov/div837/Division/outputs/DTSA/DTSA.htm")
    THINH_LEROUS1979 = ('Thinh and Leroux' , 'Thinh and Leroux (1979)',)
    LLNL1989 = ('LLNL Evaluated Photon Data Library', 'Lawrence Livermore National Laboratory. (1989). Tables and graphs of photon-interaction cross sections from 10 eV to 100 GeV derived from the LLNL evaluated photon data library EPDL. Livermore, CA: Cullen, D., Chen, M., Hubbell, J., Perkins, S., Plechaty, E., Rathkopf, J., & Scofield, J..')

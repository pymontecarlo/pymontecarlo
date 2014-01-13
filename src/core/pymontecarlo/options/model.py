#!/usr/bin/env python
"""
================================================================================
:mod:`model` -- Algorithm models
================================================================================

.. module:: model
   :synopsis: Algorithm models

.. inheritance-diagram:: pymontecarlo.input.model

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['BREMSSTRAHLUNG_EMISSION',
           'DIRECTION_COSINE',
           'ELASTIC_CROSS_SECTION',
           'ENERGY_LOSS',
           'FLUORESCENCE',
           'INELASTIC_CROSS_SECTION',
           'IONIZATION_CROSS_SECTION',
           'IONIZATION_POTENTIAL',
           'MASS_ABSORPTION_COEFFICIENT',
           'PHOTON_SCATTERING_CROSS_SECTION',
           'RANDOM_NUMBER_GENERATOR']

# Standard library modules.
import collections

# Third party modules.

# Local modules.
from pymontecarlo.options.xmlmapper import \
    mapper, _XMLType, Attribute, PythonType

# Globals and constants variables.

_type_registry = {}

class ModelType(collections.Set):

    def __new__(cls, name):
        if name in _type_registry:
            return _type_registry[name]

        # New type
        type_ = super(ModelType, cls).__new__(cls)
        object.__setattr__(type_, '_name', name)
        object.__setattr__(type_, '_models', set())
        object.__setattr__(type_, '_modelnames', {})
        _type_registry[name] = type_
        return type_

    def __len__(self):
        return len(self._models)

    def __iter__(self):
        return iter(self._models)

    def __contains__(self, model):
        if isinstance(model, Model):
            return model in self._models
        else:
            return model in self._modelnames

    def __setattr__(self, name, value):
        model = Model(self, *value)

        if name in self.__dict__:
            raise ValueError, "Model '%s' is already registered" % name
        if model in self._models:
            raise ValueError, "Model '%s' is already registered" % model

        self._models.add(model)
        self._modelnames[model.name] = model
        object.__setattr__(self, name, model)

    def __repr__(self):
        return '<ModelType(%s)>' % self._name

    def __str__(self):
        return self._name

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return self._name == other._name

    def __ne__(self, other):
        return not self == other

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        return self

class _ModelXMLType(_XMLType):

    def to_xml(self, type_):
        return str(type_)

    def from_xml(self, name):
        return ModelType(name)

class Model(object):

    def __new__(cls, type, name, reference=''): # @ReservedAssignment
        if name in type:
            return type._modelnames[name]

        model = super(Model, cls).__new__(cls)
        model._type = type
        model._name = name
        model._reference = reference
        return model

    def __repr__(self):
        return '<Model(%s)>' % self._name

    def __str__(self):
        return self._name

    def __hash__(self):
        return hash((self._name, self._type))

    def __eq__(self, other):
        return self._name == other._name and self._type == other._type

    def __ne__(self, other):
        return not self == other

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        return self

    @property
    def name(self):
        return self._name

    @property
    def reference(self):
        return self._reference

    @property
    def type(self):
        return self._type

mapper.register(Model, "{http://pymontecarlo.sf.net}model",
                Attribute('type', _ModelXMLType()),
                Attribute('name', PythonType(str)))

#-------------------------------------------------------------------------------

ELASTIC_CROSS_SECTION = ModelType('elastic cross section')

ELASTIC_CROSS_SECTION.mott_czyzewski1990 = \
    ('Mott by interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_czyzewski1990_linear = \
    ('Mott by linear interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_czyzewski1990_powerlaw = \
    ('Mott by power law interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_czyzewski1990_cubicspline = \
    ('Mott by cubic spline interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_demers = \
    ('Mott parametrized (Demers)', 'Demers')
ELASTIC_CROSS_SECTION.mott_drouin1993 = \
    ('Mott by equation (Drouin)', 'Drouin and Gauvin (1993)')
ELASTIC_CROSS_SECTION.mott_browning1994 = \
    ('Mott by equation (Browning)', 'Browning (1994)')
ELASTIC_CROSS_SECTION.rutherford = ('Rutherford',)
ELASTIC_CROSS_SECTION.rutherford_relativistic = ('Rutherford relativistic',)
ELASTIC_CROSS_SECTION.elsepa2005 = ('ELSEPA', 'Salvat, F., Jablonski, A., & Powell, C. (2005). ELSEPA - Dirac partial-wave calculation of elastic scattering of electrons and positrons by atoms, positive ions and molecules. Comput. Phys. Commun., 165, 157-190.')
ELASTIC_CROSS_SECTION.reimer = ('Reimer',)

#-------------------------------------------------------------------------------

INELASTIC_CROSS_SECTION = ModelType('inelastic cross section')

INELASTIC_CROSS_SECTION.sternheimer_liljequist1952 = \
    ('Sternheimer-Liljequist generalised oscillator strength', 'Sternheimer, R. (1952). The density effect for the ionization loss in various materials. Phys. Rev., 88, 851-859. AND Liljequist, D. (1983). A simple calculation of inelastic mean free path and stopping power for 50 eV --50 keV electrons in solids. J. Phys. D: Appl. Phys., 16, 1567-1582.')

#-------------------------------------------------------------------------------

IONIZATION_CROSS_SECTION = ModelType('ionization cross section')

IONIZATION_CROSS_SECTION.gauvin = ('Gauvin',)
IONIZATION_CROSS_SECTION.pouchou1986 = \
    ('Pouchou 1986', "Pochou & Pichoir in the proceedings from IXCOM 11 (1986)")
IONIZATION_CROSS_SECTION.brown_powell = ('Brown Powell',)
IONIZATION_CROSS_SECTION.casnati1982 = \
    ('Casnati 1982', "Casnati82 - E. Casnati, A. Tartari & C. Baraldi, J Phys B15 (1982) 155 as quoted by C. Powell in Ultramicroscopy 28 (1989) 24-31")
IONIZATION_CROSS_SECTION.gryzinsky = ('Gryzinsky',)
IONIZATION_CROSS_SECTION.gryzinsky_bethe = ('Gryzinsky + Bethe',)
IONIZATION_CROSS_SECTION.jakoby = ('Jakoby',)
IONIZATION_CROSS_SECTION.bote_salvat2008 = \
    ('Bote and Salvat 2008', 'Bote and Salvat (2008)')
IONIZATION_CROSS_SECTION.dijkstra_heijliger1998 = \
    ("Dijkstra and Heijliger 1998 (PROZA96)", "G.F. Bastin, J. M. Dijkstra and H.J.M. Heijligers (1998). X-Ray Spectrometry, 27, pp. 3-10")
IONIZATION_CROSS_SECTION.worthington_tomlin1956 = \
    ('Worthington and Tomlin 1956', 'C.R. Worthington and S.G. Tomlin (1956) The intensity of emission of characteristic x-radiation, Proc. Phys. Soc. A-69, p.401')
IONIZATION_CROSS_SECTION.hutchins1974 = \
    ('Hutchins 1974', 'G.A. Hutchins (1974) Electron Probe Microanalysis, in P.F. Kane and G.B. Larrabee, Characterisation of solid surfaces, Plenum Press, New York, p. 441')

#-------------------------------------------------------------------------------

BREMSSTRAHLUNG_EMISSION = ModelType('Bremsstrahlung emission')

BREMSSTRAHLUNG_EMISSION.seltzer_berger1985 = \
    ('Seltzer and Berger', 'Seltzer, S., & Berger, M. (1985). Bremsstrahlung spectra from electron interactions with screened atomic nuclei and orbital electrons. Nucl. Instrum. Meth. B, 12, 95-134.')

#-------------------------------------------------------------------------------

IONIZATION_POTENTIAL = ModelType('ionization potential')

IONIZATION_POTENTIAL.joy_luo1989 = ('Joy and Luo', 'Joy and Luo (1989)')
IONIZATION_POTENTIAL.berger_seltzer1964 = \
    ("Berger & Seltzer 1964", "Berger MJ, Seltzer S. NASA Technical Publication SP-4012 (1964)")
IONIZATION_POTENTIAL.berger_seltzer1983 = \
    ("Berger & Seltzer 1983", "Berger MJ, Seltzer S. NBSIR 82-2550-A - US Dept of Commerce, Washington DC (1983)")
IONIZATION_POTENTIAL.berger_seltzer1983_citzaf = \
    ("Berger & Seltzer 1983 (CITZAF)", "Berger and Seltzer as implemented by CITZAF 3.06")
IONIZATION_POTENTIAL.zeller1975 = \
    ("Zeller 1975", "Zeller C in Ruste J, Gantois M, J. Phys. D. Appl. Phys 8, 872 (1975)")
IONIZATION_POTENTIAL.duncumb_decasa1969 = \
    ("Duncumb & DeCasa 1969", "Duncumb P, Shields-Mason PK, DeCasa C. Proc. 5th Int. Congr. on X-ray Optics and Microanalysis, Springer, Berlin, 1969 p. 146")
IONIZATION_POTENTIAL.heinrich_yakowitz1970 = \
    ("Heinrich & Yakowitz 1970", "Heinrich KFJ, Yakowitz H. Mikrochim Acta (1970) p 123")
IONIZATION_POTENTIAL.springer1967 = \
    ("Springer 1967", "Springer G. Meues Jahrbuch Fuer Mineralogie, Monatshefte (1967) 9/10, p. 304")
IONIZATION_POTENTIAL.wilson1941 = \
    ("Wilson 1941", "Wilson RR. Phys Rev. 60. 749 (1941)")
IONIZATION_POTENTIAL.bloch1933 = \
    ("Bloch 1933", "Bloch F, F. Z. Phys. 81, 363 (1933)")
IONIZATION_POTENTIAL.sternheimer1964 = \
    ("Sternheimer 1964", "Sternheimer quoted in Berger MJ, Seltzer S. NASA Technical Publication SP-4012 (1964)")
IONIZATION_POTENTIAL.hovington = ('Hovington',)
IONIZATION_POTENTIAL.gryzinski = ('Gryzinski',)

#-------------------------------------------------------------------------------

RANDOM_NUMBER_GENERATOR = ModelType('random number generator')

RANDOM_NUMBER_GENERATOR.press1966_rand1 = \
    ('Press et al. - rand1', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press1966_rand2 = \
    ('Press et al. - rand2', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press1966_rand3 = \
    ('Press et al. - rand3', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press1966_rand4 = \
    ('Press et al. - rand4', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.mersenne = ('Mersenne - Twister',)
RANDOM_NUMBER_GENERATOR.lagged_fibonacci = ('Lagged Fibonacci (Boost If607)',)

#-------------------------------------------------------------------------------

DIRECTION_COSINE = ModelType('direction cosine')

DIRECTION_COSINE.soum1979 = ('Soum et al.', 'Soum et al. (1979)')
DIRECTION_COSINE.drouin1996 = ('Drouin', 'Drouin (1996)')
DIRECTION_COSINE.demers2000 = ('Demers - Matrices rotation', 'Demers (2000)')
DIRECTION_COSINE.lowney1994 = ('Lowney (1994)',)

#-------------------------------------------------------------------------------

PHOTON_SCATTERING_CROSS_SECTION = ModelType('photon scattering cross section')

PHOTON_SCATTERING_CROSS_SECTION.brusa1996 = \
    ('Brusa et al. photon compton scattering', 'Brusa, D., Stutz, G., Riveros, J., Fernandez-Vera, J., & Salvat, F. (1996). Fast sampling algorithm for the simulation of photon compton scattering. Nucl. Instrum. Meth. A, 379, 167-175.')

#-------------------------------------------------------------------------------

ENERGY_LOSS = ModelType('energy loss')

ENERGY_LOSS.joy_luo1989 = ('Joy and Luo 1989', 'Joy and Luo (1989)')
ENERGY_LOSS.bethe1930 = \
    ("Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
ENERGY_LOSS.bethe1930mod = \
    ("Modified Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
ENERGY_LOSS.joy_luo_lowney = ('Joy and Luo + Lowney',)

#-------------------------------------------------------------------------------

MASS_ABSORPTION_COEFFICIENT = ModelType('mass absorption coefficient')

MASS_ABSORPTION_COEFFICIENT.none = ('No MAC',)
MASS_ABSORPTION_COEFFICIENT.ruste1979 = \
    ('Ruste 1979', 'J. Ruste, J. Microsc. Spectrosc. Electron. 4, 123 (1979)')
MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991 = \
    ('Pouchou and Pichoir 1991', 'Pouchou & Pichoir in Electron Probe Quantitation, Eds Heinrich and Newbury')
MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1988 = \
    ('Pouchou and Pichoir 1988', "J. L. Pouchou and F. M. A. Pichoir, 'Determination of Mass Absorption Coefficients for Soft X-Rays by use of the Electron Microprobe' Microbeam Analysis, Ed. D. E. Newbury, San Francisco Press, 1988, p. 319-324")
MASS_ABSORPTION_COEFFICIENT.henke1982 = \
    ('Henke 1982', "B. L. Henke, P. Lee, T. J. Tanaka, R. L. Shimabukuro and B. K. Fijikawa, Atomic Data Nucl. Data Tables 27, 1 (1982)")
MASS_ABSORPTION_COEFFICIENT.henke1993 = \
    ('Henke 1993', "B.L. Henke, E.M. Gullikson and J.C. Davis (1993). X-ray interactions: photoabsorption, scattering, transmission, and reflection at E=50-30000 eV, Z=1-92, Atomic Data and Nuclear Data Tables, 54, pp. 181-342")
MASS_ABSORPTION_COEFFICIENT.bastin_heijligers1989 = \
    ('Bastin and Heijligers 1985 1988 1989', "as quoted in Scott, Love & Reed, Quantitative Electron-Probe Microanalysis, 2nd ed.")
MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11_dtsa = \
    ('Heinrich IXCOM 11 (DTSA)', "Heinrich KFJ. in Proc. 11th Int. Congr. X-ray Optics & Microanalysis, Brown JD, Packwood RH (eds). Univ. Western Ontario: London, 1986; 67")
MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11 = \
    ('Heinrich IXCOM 11', "Heinrich KFJ. in Proc. 11th Int. Congr. X-ray Optics & Microanalysis, Brown JD, Packwood RH (eds). Univ. Western Ontario: London, 1986; 67")
MASS_ABSORPTION_COEFFICIENT.chantler2005 = \
    ('NIST-Chantler 2005', "See http://physics.nist.gov/ffast")
MASS_ABSORPTION_COEFFICIENT.dtsa_citzaf = \
    ('DTSA CitZAF', "DTSA at http://www.cstl.nist.gov/div837/Division/outputs/DTSA/DTSA.htm")
MASS_ABSORPTION_COEFFICIENT.thinh_leroux1979 = \
    ('Thinh and Leroux' , 'Thinh and Leroux (1979)',)
MASS_ABSORPTION_COEFFICIENT.llnl1989 = \
    ('LLNL Evaluated Photon Data Library', 'Lawrence Livermore National Laboratory. (1989). Tables and graphs of photon-interaction cross sections from 10 eV to 100 GeV derived from the LLNL evaluated photon data library EPDL. Livermore, CA: Cullen, D., Chen, M., Hubbell, J., Perkins, S., Plechaty, E., Rathkopf, J., & Scofield, J..')

#-------------------------------------------------------------------------------

FLUORESCENCE = ModelType("fluorescence")

FLUORESCENCE.none = ('no fluorescence',)
FLUORESCENCE.fluorescence = ('fluorescence',)
FLUORESCENCE.fluorescence_compton = ('fluorescence with Compton',)

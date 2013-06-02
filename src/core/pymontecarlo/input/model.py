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

__all__ = ['get_all_models',
           'BREMSSTRAHLUNG_EMISSION',
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
from pymontecarlo.util.xmlutil import XMLIO
from pymontecarlo.input.option import Option

# Globals and constants variables.

_model_registry = {}

def get_all_models():
    return _model_registry.values()

class ModelType(collections.Set):
    def __init__(self, name):
        self._name = name
        self._models = {}

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

    def __len__(self):
        return len(self._models)

    def __iter__(self):
        return self._models.itervalues()

    def __contains__(self, model):
        return model in self._models.values()

    @property
    def name(self):
        return self._name

    def register(self, model):
        model._register(self)
        key = hash(model)

        if key in self._models:
            raise ValueError, "Model with name (%s) is already registered for this type" % \
                model.name

        _model_registry[key] = model
        self._models.setdefault(key, model)

class __NoModelType(ModelType):
    def __init__(self):
        ModelType.__init__(self, 'no type')

    def __nonzero__(self):
        return False

    def register(self, model):
        raise ValueError, 'Cannot register model to the NO_MODEL_TYPE'

NO_MODEL_TYPE = __NoModelType()

class Model(Option):
    def __init__(self, name, reference=''):
        Option.__init__(self)

        self._name = name
        self._reference = reference
        self._type = NO_MODEL_TYPE

    @staticmethod
    def __hash(name, type):
        return hash((name, type))

    def __repr__(self):
        return '<Model(%s)>' % self._name

    def __str__(self):
        return self._name

    def __hash__(self):
        return self.__hash(self._name, self._type)

    def __eq__(self, other):
        return self._name == other._name and self._type == other._type

    def __ne__(self, other):
        return not self == other

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        name = element.get('name')
        type = element.get('type')
        hash = cls.__hash(name, type)

        try:
            return _model_registry[hash]
        except KeyError:
            raise IOError, "Model not found"

    def __savexml__(self, element, *args, **kwargs):
        if not self._type:
            raise IOError, "Cannot saved unregistered model"
        element.set('name', self._name)
        element.set('type', str(self._type))

    def _register(self, type):
        self._type = type

    @property
    def name(self):
        return self._name

    @property
    def reference(self):
        return self._reference

    @property
    def type(self):
        if not self._type:
            raise ValueError, "No type. Model is unregistered."
        return self._type

XMLIO.register('{http://pymontecarlo.sf.net}model', Model)

class ModelCategory(collections.Set):

    def __init__(self, type):
        object.__setattr__(self, '_type', type)
        object.__setattr__(self, '_models', set())

    def __len__(self):
        return len(self._models)

    def __iter__(self):
        return iter(self._models)

    def __contains__(self, model):
        return model in self._models

    def __setattr__(self, name, model):
        self._type.register(model)

        if model in self._models:
            raise ValueError, "Model with name (%s) is already registered" % \
                model.name
        self._models.add(model)

        object.__setattr__(self, name, model)

    @property
    def type(self):
        return self._type

#-------------------------------------------------------------------------------

ELASTIC_CROSS_SECTION_TYPE = ModelType('elastic cross section')

ELASTIC_CROSS_SECTION = ModelCategory(ELASTIC_CROSS_SECTION_TYPE)
ELASTIC_CROSS_SECTION.mott_czyzewski1990 = \
    Model('Mott by interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_czyzewski1990_linear = \
    Model('Mott by linear interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_czyzewski1990_powerlaw = \
    Model('Mott by power law interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_czyzewski1990_cubicspline = \
    Model('Mott by cubic spline interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_demers = \
    Model('Mott parametrized (Demers)', 'Demers')
ELASTIC_CROSS_SECTION.mott_drouin1993 = \
    Model('Mott by equation (Drouin)', 'Drouin and Gauvin (1993)')
ELASTIC_CROSS_SECTION.mott_browning1994 = \
    Model('Mott by equation (Browning)', 'Browning (1994)')
ELASTIC_CROSS_SECTION.rutherford = Model('Rutherford')
ELASTIC_CROSS_SECTION.rutherford_relativistic = Model('Rutherford relativistic')
ELASTIC_CROSS_SECTION.elsepa2005 = Model('ELSEPA', 'Salvat, F., Jablonski, A., & Powell, C. (2005). ELSEPA - Dirac partial-wave calculation of elastic scattering of electrons and positrons by atoms, positive ions and molecules. Comput. Phys. Commun., 165, 157-190.')
ELASTIC_CROSS_SECTION.reimer = Model('Reimer')

#-------------------------------------------------------------------------------

INELASTIC_CROSS_SECTION_TYPE = ModelType('inelastic cross section')

INELASTIC_CROSS_SECTION = ModelCategory(INELASTIC_CROSS_SECTION_TYPE)
INELASTIC_CROSS_SECTION.sternheimer_liljequist1952 = \
    Model('Sternheimer-Liljequist generalised oscillator strength', 'Sternheimer, R. (1952). The density effect for the ionization loss in various materials. Phys. Rev., 88, 851-859. AND Liljequist, D. (1983). A simple calculation of inelastic mean free path and stopping power for 50 eV --50 keV electrons in solids. J. Phys. D: Appl. Phys., 16, 1567-1582.')

#-------------------------------------------------------------------------------

IONIZATION_CROSS_SECTION_TYPE = ModelType('ionization cross section')

IONIZATION_CROSS_SECTION = ModelCategory(IONIZATION_CROSS_SECTION_TYPE)
IONIZATION_CROSS_SECTION.gauvin = Model('Gauvin')
IONIZATION_CROSS_SECTION.pouchou1986 = \
    Model('Pouchou 1986', "Pochou & Pichoir in the proceedings from IXCOM 11 (1986)")
IONIZATION_CROSS_SECTION.brown_powell = Model('Brown Powell')
IONIZATION_CROSS_SECTION.casnati1982 = \
    Model('Casnati 1982', "Casnati82 - E. Casnati, A. Tartari & C. Baraldi, J Phys B15 (1982) 155 as quoted by C. Powell in Ultramicroscopy 28 (1989) 24-31")
IONIZATION_CROSS_SECTION.gryzinsky = Model('Gryzinsky')
IONIZATION_CROSS_SECTION.gryzinsky_bethe = Model('Gryzinsky + Bethe')
IONIZATION_CROSS_SECTION.jakoby = Model('Jakoby')
IONIZATION_CROSS_SECTION.bote_salvat2008 = \
    Model('Bote and Salvat 2008', 'Bote and Salvat (2008)')
IONIZATION_CROSS_SECTION.dijkstra_heijliger1998 = \
    Model("Dijkstra and Heijliger 1998 (PROZA96)", "G.F. Bastin, J. M. Dijkstra and H.J.M. Heijligers (1998). X-Ray Spectrometry, 27, pp. 3-10")
IONIZATION_CROSS_SECTION.worthington_tomlin1956 = \
    Model('Worthington and Tomlin 1956', 'C.R. Worthington and S.G. Tomlin (1956) The intensity of emission of characteristic x-radiation, Proc. Phys. Soc. A-69, p.401')
IONIZATION_CROSS_SECTION.hutchins1974 = \
    Model('Hutchins 1974', 'G.A. Hutchins (1974) Electron Probe Microanalysis, in P.F. Kane and G.B. Larrabee, Characterisation of solid surfaces, Plenum Press, New York, p. 441')

#-------------------------------------------------------------------------------

BREMSSTRAHLUNG_EMISSION_TYPE = ModelType('Bremsstrahlung emission')

BREMSSTRAHLUNG_EMISSION = ModelCategory(BREMSSTRAHLUNG_EMISSION_TYPE)
BREMSSTRAHLUNG_EMISSION.seltzer_berger1985 = \
    Model('Seltzer and Berger', 'Seltzer, S., & Berger, M. (1985). Bremsstrahlung spectra from electron interactions with screened atomic nuclei and orbital electrons. Nucl. Instrum. Meth. B, 12, 95-134.')

#-------------------------------------------------------------------------------

IONIZATION_POTENTIAL_TYPE = ModelType('ionization potential')

IONIZATION_POTENTIAL = ModelCategory(IONIZATION_POTENTIAL_TYPE)
IONIZATION_POTENTIAL.joy_luo1989 = Model('Joy and Luo', 'Joy and Luo (1989)')
IONIZATION_POTENTIAL.berger_seltzer1964 = \
    Model("Berger & Seltzer 1964", "Berger MJ, Seltzer S. NASA Technical Publication SP-4012 (1964)")
IONIZATION_POTENTIAL.berger_seltzer1983 = \
    Model("Berger & Seltzer 1983", "Berger MJ, Seltzer S. NBSIR 82-2550-A - US Dept of Commerce, Washington DC (1983)")
IONIZATION_POTENTIAL.berger_seltzer1983_citzaf = \
    Model("Berger & Seltzer 1983 (CITZAF)", "Berger and Seltzer as implemented by CITZAF 3.06")
IONIZATION_POTENTIAL.zeller1975 = \
    Model("Zeller 1975", "Zeller C in Ruste J, Gantois M, J. Phys. D. Appl. Phys 8, 872 (1975)")
IONIZATION_POTENTIAL.duncumb_decasa1969 = \
    Model("Duncumb & DeCasa 1969", "Duncumb P, Shields-Mason PK, DeCasa C. Proc. 5th Int. Congr. on X-ray Optics and Microanalysis, Springer, Berlin, 1969 p. 146")
IONIZATION_POTENTIAL.heinrich_yakowitz1970 = \
    Model("Heinrich & Yakowitz 1970", "Heinrich KFJ, Yakowitz H. Mikrochim Acta (1970) p 123")
IONIZATION_POTENTIAL.springer1967 = \
    Model("Springer 1967", "Springer G. Meues Jahrbuch Fuer Mineralogie, Monatshefte (1967) 9/10, p. 304")
IONIZATION_POTENTIAL.wilson1941 = \
    Model("Wilson 1941", "Wilson RR. Phys Rev. 60. 749 (1941)")
IONIZATION_POTENTIAL.bloch1933 = \
    Model("Bloch 1933", "Bloch F, F. Z. Phys. 81, 363 (1933)")
IONIZATION_POTENTIAL.sternheimer1964 = \
    Model("Sternheimer 1964", "Sternheimer quoted in Berger MJ, Seltzer S. NASA Technical Publication SP-4012 (1964)")
IONIZATION_POTENTIAL.hovington = Model('Hovington')
IONIZATION_POTENTIAL.gryzinski = Model('Gryzinski')

#-------------------------------------------------------------------------------

RANDOM_NUMBER_GENERATOR_TYPE = ModelType('random number generator')

RANDOM_NUMBER_GENERATOR = ModelCategory(RANDOM_NUMBER_GENERATOR_TYPE)
RANDOM_NUMBER_GENERATOR.press1966_rand1 = \
    Model('Press et al. - rand1', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press1966_rand2 = \
    Model('Press et al. - rand2', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press1966_rand3 = \
    Model('Press et al. - rand3', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press1966_rand4 = \
    Model('Press et al. - rand4', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.mersenne = Model('Mersenne - Twister')
RANDOM_NUMBER_GENERATOR.lagged_fibonacci = Model ('Lagged Fibonacci (Boost If607)')

#-------------------------------------------------------------------------------

DIRECTION_COSINE_TYPE = ModelType('direction cosine')

DIRECTION_COSINE = ModelCategory(DIRECTION_COSINE_TYPE)
DIRECTION_COSINE.soum1979 = Model('Soum et al.', 'Soum et al. (1979)')
DIRECTION_COSINE.drouin1996 = Model('Drouin', 'Drouin (1996)')
DIRECTION_COSINE.demers2000 = Model('Demers - Matrices rotation', 'Demers (2000)')
DIRECTION_COSINE.lowney1994 = Model('Lowney (1994)')

#-------------------------------------------------------------------------------

PHOTON_SCATTERING_CROSS_SECTION_TYPE = ModelType('photon scattering cross section')

PHOTON_SCATTERING_CROSS_SECTION = ModelCategory(PHOTON_SCATTERING_CROSS_SECTION_TYPE)
PHOTON_SCATTERING_CROSS_SECTION.brusa1996 = \
    Model('Brusa et al. photon compton scattering', 'Brusa, D., Stutz, G., Riveros, J., Fernandez-Vera, J., & Salvat, F. (1996). Fast sampling algorithm for the simulation of photon compton scattering. Nucl. Instrum. Meth. A, 379, 167-175.')

#-------------------------------------------------------------------------------

ENERGY_LOSS_TYPE = ModelType('energy loss')

ENERGY_LOSS = ModelCategory(ENERGY_LOSS_TYPE)
ENERGY_LOSS.joy_luo1989 = Model('Joy and Luo 1989', 'Joy and Luo (1989)')
ENERGY_LOSS.bethe1930 = \
    Model("Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
ENERGY_LOSS.bethe1930mod = \
    Model("Modified Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
ENERGY_LOSS.joy_luo_lowney = Model('Joy and Luo + Lowney')

#-------------------------------------------------------------------------------

MASS_ABSORPTION_COEFFICIENT_TYPE = ModelType('mass absorption coefficient')

MASS_ABSORPTION_COEFFICIENT = ModelCategory(MASS_ABSORPTION_COEFFICIENT_TYPE)
MASS_ABSORPTION_COEFFICIENT.none = Model('No MAC')
MASS_ABSORPTION_COEFFICIENT.ruste1979 = \
    Model('Ruste 1979', 'J. Ruste, J. Microsc. Spectrosc. Electron. 4, 123 (1979)')
MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991 = \
    Model('Pouchou and Pichoir 1991', 'Pouchou & Pichoir in Electron Probe Quantitation, Eds Heinrich and Newbury')
MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1988 = \
    Model('Pouchou and Pichoir 1988', "J. L. Pouchou and F. M. A. Pichoir, 'Determination of Mass Absorption Coefficients for Soft X-Rays by use of the Electron Microprobe' Microbeam Analysis, Ed. D. E. Newbury, San Francisco Press, 1988, p. 319-324")
MASS_ABSORPTION_COEFFICIENT.henke1982 = \
    Model('Henke 1982', "B. L. Henke, P. Lee, T. J. Tanaka, R. L. Shimabukuro and B. K. Fijikawa, Atomic Data Nucl. Data Tables 27, 1 (1982)")
MASS_ABSORPTION_COEFFICIENT.henke1993 = \
    Model('Henke 1993', "B.L. Henke, E.M. Gullikson and J.C. Davis (1993). X-ray interactions: photoabsorption, scattering, transmission, and reflection at E=50-30000 eV, Z=1-92, Atomic Data and Nuclear Data Tables, 54, pp. 181-342")
MASS_ABSORPTION_COEFFICIENT.bastin_heijligers1989 = \
    Model('Bastin and Heijligers 1985, 1988, 1989', "as quoted in Scott, Love & Reed, Quantitative Electron-Probe Microanalysis, 2nd ed.")
MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11_dtsa = \
    Model('Heinrich IXCOM 11 (DTSA)', "Heinrich KFJ. in Proc. 11th Int. Congr. X-ray Optics & Microanalysis, Brown JD, Packwood RH (eds). Univ. Western Ontario: London, 1986; 67")
MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11 = \
    Model('Heinrich IXCOM 11', "Heinrich KFJ. in Proc. 11th Int. Congr. X-ray Optics & Microanalysis, Brown JD, Packwood RH (eds). Univ. Western Ontario: London, 1986; 67")
MASS_ABSORPTION_COEFFICIENT.chantler2005 = \
    Model('NIST-Chantler 2005', "See http://physics.nist.gov/ffast")
MASS_ABSORPTION_COEFFICIENT.dtsa_citzaf = \
    Model('DTSA CitZAF', "DTSA at http://www.cstl.nist.gov/div837/Division/outputs/DTSA/DTSA.htm")
MASS_ABSORPTION_COEFFICIENT.thinh_leroux1979 = \
    Model('Thinh and Leroux' , 'Thinh and Leroux (1979)')
MASS_ABSORPTION_COEFFICIENT.llnl1989 = \
    Model('LLNL Evaluated Photon Data Library', 'Lawrence Livermore National Laboratory. (1989). Tables and graphs of photon-interaction cross sections from 10 eV to 100 GeV derived from the LLNL evaluated photon data library EPDL. Livermore, CA: Cullen, D., Chen, M., Hubbell, J., Perkins, S., Plechaty, E., Rathkopf, J., & Scofield, J..')

#-------------------------------------------------------------------------------

FLUORESCENCE_TYPE = ModelType("fluorescence")

FLUORESCENCE = ModelCategory(FLUORESCENCE_TYPE)
FLUORESCENCE.none = Model('no fluorescence')
FLUORESCENCE.fluorescence = Model('fluorescence')
FLUORESCENCE.fluorescence_compton = Model('fluorescence with Compton')

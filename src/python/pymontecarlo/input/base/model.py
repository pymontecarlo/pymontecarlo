#!/usr/bin/env python
"""
================================================================================
:mod:`module_name` -- module_desc
================================================================================

.. module:: module_name
   :synopsis: module_desc

.. inheritance-diagram:: module_name

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import collections

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlutil import objectxml

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

NO_MODEL_TYPE = __NoModelType()

class Model(objectxml):
    def __init__(self, name, reference=''):
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
ELASTIC_CROSS_SECTION.mott_czyzewski = \
    Model('Mott by interpolation (Czyzewski)', 'Czyzewski (1990)')
ELASTIC_CROSS_SECTION.mott_drouin = \
    Model('Mott by equation (Drouin)', 'Drouin and Gauvin (1993)')
ELASTIC_CROSS_SECTION.mott_browning = \
    Model('Mott by equation (Browning)', 'Browning (1994)')
ELASTIC_CROSS_SECTION.rutherford = Model('Rutherford')

#-------------------------------------------------------------------------------

IONIZATION_CROSS_SECTION_TYPE = ModelType('ionization cross section')

IONIZATION_CROSS_SECTION = ModelCategory(IONIZATION_CROSS_SECTION_TYPE)
IONIZATION_CROSS_SECTION.gauvin = Model('Gauvin')
IONIZATION_CROSS_SECTION.pouchou = Model('Pouchou')
IONIZATION_CROSS_SECTION.brown_powell = Model('Brown Powell')
IONIZATION_CROSS_SECTION.casnati = Model('Casnati')
IONIZATION_CROSS_SECTION.gryzinsky = Model('Gryzinsky')
IONIZATION_CROSS_SECTION.jakoby = Model('Jakoby')
IONIZATION_CROSS_SECTION.bote_salvat = \
    Model('Bote and Salvat', 'Bote and Salvat (2008)')

#-------------------------------------------------------------------------------

IONIZATION_POTENTIAL_TYPE = ModelType('ionization potential')

IONIZATION_POTENTIAL = ModelCategory(IONIZATION_POTENTIAL_TYPE)
IONIZATION_POTENTIAL.joy_luo = Model('Joy and Luo', 'Joy and Luo (1989)')
IONIZATION_POTENTIAL.berger_seltzer = \
    Model('Berger and Seltzer', 'Berger and Seltzer (1964)')
IONIZATION_POTENTIAL.hovington = Model('Hovington')

#-------------------------------------------------------------------------------

RANDOM_NUMBER_GENERATOR_TYPE = ModelType('random number generator')

RANDOM_NUMBER_GENERATOR = ModelCategory(RANDOM_NUMBER_GENERATOR_TYPE)
RANDOM_NUMBER_GENERATOR.press_rand1 = \
    Model('Press et al. - rand1', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press_rand2 = \
    Model('Press et al. - rand2', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press_rand3 = \
    Model('Press et al. - rand3', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.press_rand4 = \
    Model('Press et al. - rand4', 'Press et al. (1966)')
RANDOM_NUMBER_GENERATOR.mersenne = Model('Mersenne - Twister')

#-------------------------------------------------------------------------------

DIRECTION_COSINE_TYPE = ModelType('direction cosine')

DIRECTION_COSINE = ModelCategory(DIRECTION_COSINE_TYPE)
DIRECTION_COSINE.soum = Model('Soum et al.', 'Soum et al. (1979)')
DIRECTION_COSINE.drouin = Model('Drouin', 'Drouin (1996)')
DIRECTION_COSINE.demers = Model('Demers - Matrices rotation', 'Demers (2000)')

#-------------------------------------------------------------------------------

ENERGY_LOSS_TYPE = ModelType('energy loss')

ENERGY_LOSS = ModelCategory(ENERGY_LOSS_TYPE)
ENERGY_LOSS.joy_luo = Model('Joy and Luo', 'Joy and Luo (1989)')

#-------------------------------------------------------------------------------

MASS_ABSORPTION_COEFFICIENT_TYPE = ModelType('mass absorption coefficient')

MASS_ABSORPTION_COEFFICIENT = ModelCategory(MASS_ABSORPTION_COEFFICIENT_TYPE)
MASS_ABSORPTION_COEFFICIENT.none = Model('No MAC')
MASS_ABSORPTION_COEFFICIENT.ruste1979 = \
    Model('Ruste 1979', 'J. Ruste, J. Microsc. Spectrosc. Electron. 4, 123 (1979)')
MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1991 = \
    Model('Pouchou and Pichoir 1991', 'Pouchou & Pichoir in Electron Probe Quantitation, Eds Heinrich and Newbury')
MASS_ABSORPTION_COEFFICIENT.pouchou_pichoir1988 = \
    Model('Pouchou adbd Pichoir 1988', "J. L. Pouchou and F. M. A. Pichoir, 'Determination of Mass Absorption Coefficients for Soft X-Rays by use of the Electron Microprobe' Microbeam Analysis, Ed. D. E. Newbury, San Francisco Press, 1988, p. 319-324")
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
    Model('DSTA CitZAF', "DTSA at http://www.cstl.nist.gov/div837/Division/outputs/DTSA/DTSA.htm")
MASS_ABSORPTION_COEFFICIENT.thinh_leroux = \
    Model('Thinh and Leroux' , 'Thinh and Leroux (1979)')

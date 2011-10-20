#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.util.relaxation_data import RelaxationData, Transition, Subshell

# Globals and constants variables.
from pymontecarlo.util.relaxation_data import \
    (SHELL_IUPACS, SHELL_ORBITALS, SHELL_SIEGBAHNS,
     TRANSITION_SHELLS, TRANSITION_SIEGBAHNS_NOGREEK, TRANSITION_SIEGBAHNS)

class TestSubshell(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        for i in range(1, 31):
            setattr(self, 's%i' % i, Subshell(index=i))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testindex(self):
        for i in range(1, 31):
            self.assertEqual(i, getattr(self, 's%i' % i).index)

    def testorbital(self):
        for i in range(1, 31):
            self.assertEqual(SHELL_ORBITALS[i - 1], getattr(self, 's%i' % i).orbital)

    def testiupac(self):
        for i in range(1, 31):
            self.assertEqual(SHELL_IUPACS[i - 1], getattr(self, 's%i' % i).iupac)

    def testsiegbahn(self):
        for i in range(1, 31):
            self.assertEqual(SHELL_SIEGBAHNS[i - 1], getattr(self, 's%i' % i).siegbahn)

    def testfamily(self):
        # K
        self.assertEqual('K', getattr(self, 's1').family)

        # L
        for i in range(2, 5):
            self.assertEqual("L", getattr(self, "s%i" % i).family)

        # M
        for i in range(5, 10):
            self.assertEqual("M", getattr(self, "s%i" % i).family)

        # N
        for i in range(10, 17):
            self.assertEqual("N", getattr(self, "s%i" % i).family)

        # O
        for i in range(17, 24):
            self.assertEqual("O", getattr(self, "s%i" % i).family)

        # P
        for i in range(24, 29):
            self.assertEqual("P", getattr(self, "s%i" % i).family)

        # Q
        self.assertEqual('Q', getattr(self, 's29').family)

        # outer
        self.assertEqual(None, getattr(self, 's30').family)

    def testinit_orbital(self):
        for i, orbital in enumerate(SHELL_ORBITALS):
            s = Subshell(orbital=orbital)
            self.assertEqual(i + 1, s.index)

    def testinit_iupac(self):
        for i, iupac in enumerate(SHELL_IUPACS):
            s = Subshell(iupac=iupac)
            self.assertEqual(i + 1, s.index)

    def testinit_siegbahn(self):
        for i, siegbahn in enumerate(SHELL_SIEGBAHNS):
            s = Subshell(siegbahn=siegbahn)
            self.assertEqual(i + 1, s.index)

class TestTransition(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        for i, shells in enumerate(TRANSITION_SHELLS):
            x = Transition(13, Subshell(iupac=shells[1]), Subshell(iupac=shells[0]))
            setattr(self, 'x%i' % i, x)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__init__siegbahn(self):
        x = Transition(13, siegbahn="La1")
        self.assertEqual(13, x.z)
        self.assertEqual("Al La1", str(x))

    def test__str__(self):
        for i, siegbahn in enumerate(TRANSITION_SIEGBAHNS_NOGREEK):
            x = getattr(self, "x%i" % i)
            self.assertEqual("Al " + siegbahn, str(x))

    def test__unicode__(self):
        for i, siegbahn in enumerate(TRANSITION_SIEGBAHNS):
            x = getattr(self, "x%i" % i)
            self.assertEqual("Al " + siegbahn, unicode(x))

    def testfrom_xml(self):
        element = self.x0.to_xml()
        x0 = Transition.from_xml(element)

        self.assertEqual(13, x0.z)
        self.assertEqual('Al Ka1', str(x0))

    def testz(self):
        for i in range(len(TRANSITION_SHELLS)):
            x = getattr(self, "x%i" % i)
            self.assertEqual(13, x.z)
            self.assertEqual(13, x.atomicnumber)

    def testsrc(self):
        for i, shells in enumerate(TRANSITION_SHELLS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(Subshell(iupac=shells[1]), x.src)

    def testdest(self):
        for i, shells in enumerate(TRANSITION_SHELLS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(Subshell(iupac=shells[0]), x.dest)

    def testiupac(self):
        for i, shells in enumerate(TRANSITION_SHELLS):
            x = getattr(self, "x%i" % i)
            self.assertEqual('-'.join(shells), x.iupac)

    def testsiegbahn(self):
        for i, siegbahn in enumerate(TRANSITION_SIEGBAHNS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(siegbahn, x.siegbahn)

    def testto_xml(self):
        element = self.x0.to_xml()

        self.assertEqual(13, int(element.get('z')))
        self.assertEqual(4, int(element.get('src')))
        self.assertEqual(1, int(element.get('dest')))

class TestRelaxationData(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.relaxData = RelaxationData()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
#
    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testReadData(self):
        self.assertEquals(97, len(self.relaxData.data))
#
    def testenergy(self):
        # Test Al Ka1.
        self.assertEquals(1.48671E+03, self.relaxData.energy(13, [1, 4]))

    def testprobability(self):
        # Test Al Ka1.
        self.assertEquals(2.45528e-02, self.relaxData.probability(13, [1, 4]))

    def testtransitions(self):
        transitions = self.relaxData.transitions(13)

        self.assertEqual(11, len(transitions))

    def testtransitions2(self):
        transitions = self.relaxData.transitions(13, 1e3, 2e3)
        self.assertEqual(4, len(transitions))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

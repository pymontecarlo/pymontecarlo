""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import xml.etree.ElementTree as ElementTree

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlmapper import \
    XMLMapper, Element, ElementDict, Attribute, PythonType, UserType

# Globals and constants variables.

mapper = XMLMapper()

class Human(object):

    def __init__(self, firstname, lastname, age,
                 middlenames=None, luckynumbers=None, attributes=None):
        self.firstname = firstname
        self.lastname = lastname
        self.age = age
        if middlenames is None: middlenames = []
        self.middlenames = middlenames
        if luckynumbers is None: luckynumbers = []
        self.luckynumbers = luckynumbers
        if attributes is None: attributes = {}
        self.attributes = attributes

    def __repr__(self):
        return '<Human(%s %s aged %i)>' % (self.firstname, self.lastname, self.age)

mapper.register(Human, 'human',
                Attribute('firstname', PythonType(str)),
                Attribute('lastname', PythonType(str)),
                Attribute('middlenames', PythonType(str), iterable=True),
                Attribute('age', PythonType(int)),
                Element('luckynumbers', PythonType(int), iterable=True),
                ElementDict('attributes', PythonType(str), PythonType(str), keyxmlname='_key'))

class Family(object):

    def __init__(self, father, mother, status='Married'):
        self.father = father
        self.mother = mother
        self.status = status
        self.children = []

mapper.register(Family, 'family',
                Element('father', UserType(Human)),
                Element('mother', UserType(Human)),
                Element('status', PythonType(str)),
                Element('children', UserType(Human), iterable=True))

class TestXMLMapper(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        father = Human('John', 'Smith', 52)
        mother = Human('Mary', 'Smith', 53)
        self.family = Family(father, mother)

        self.family.children.append(Human('Steve', 'Smith', 5))
        self.family.children.append(Human('Sarah', 'Smith', 9))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testto_xml1(self):
        human = Human('Steve', 'Maclean', 5, luckynumbers=[45, 68, 78],
                      attributes={'hair': 'brown', 'eyes': 'blue'})
        element = mapper.to_xml(human)

        self.assertEqual('Steve', element.get('firstname'))
        self.assertEqual('Maclean', element.get('lastname'))
        self.assertEqual('5', element.get('age'))
        self.assertEqual('45,68,78', element.find('luckynumbers').text)
        self.assertIsNone(element.get('middlenames'))
        self.assertEqual(2, len(list(element.find('attributes'))))

    def testto_xml2(self):
        element = mapper.to_xml(self.family)
        self.assertEqual(4, len(element.findall('*')))

    def testto_xml3(self):
        father = Human('John', 'Smith', 52)
        family = Family(father, father)
        element = mapper.to_xml(family)

        subelement = list(element.find('mother'))[0]
        self.assertEqual('{xmlmapper}cache', subelement.tag)
        self.assertEqual(id(father), int(subelement.get('{xmlmapper}id')))

    def testfrom_xml1(self):
        text = '<human age="5" firstname="Steve" lastname="Maclean" />'
        element = ElementTree.fromstring(text)
        obj = mapper.from_xml(element)

        self.assertEqual('Steve', obj.firstname)
        self.assertEqual('Maclean', obj.lastname)
        self.assertEqual(5, obj.age)
        self.assertEqual(0, len(obj.luckynumbers))
        self.assertEqual(0, len(obj.middlenames))

    def testfrom_xml2(self):
        text = '''<human age="5" firstname="Steve" lastname="Maclean"
                         middlenames="L,M,P">
                      <luckynumbers>45,68,78</luckynumbers>
                      <attributes>
                          <value _key="hair">brown</value>
                          <value _key="eyes">blue</value>
                      </attributes>
                  </human>'''
        element = ElementTree.fromstring(text)
        obj = mapper.from_xml(element)

        self.assertEqual('Steve', obj.firstname)
        self.assertEqual('Maclean', obj.lastname)
        self.assertEqual(5, obj.age)
        self.assertEqual(3, len(obj.luckynumbers))
        self.assertEqual(45, obj.luckynumbers[0])
        self.assertEqual(68, obj.luckynumbers[1])
        self.assertEqual(78, obj.luckynumbers[2])
        self.assertEqual(3, len(obj.middlenames))
        self.assertEqual('L', obj.middlenames[0])
        self.assertEqual('M', obj.middlenames[1])
        self.assertEqual('P', obj.middlenames[2])
        self.assertEqual(2, len(obj.attributes))
        self.assertEqual('brown', obj.attributes['hair'])
        self.assertEqual('blue', obj.attributes['eyes'])

    def testfrom_xml3(self):
        text = '''<family xmlns:xmlmapper="xmlmapper">
                      <father>
                          <human age="52" firstname="John" lastname="Smith" xmlmapper:id="0"/>
                      </father>
                      <mother>
                          <human age="53" firstname="Mary" lastname="Smith" xmlmapper:id="1"/>
                      </mother>
                      <status>Married</status>
                  </family>'''
        element = ElementTree.fromstring(text)
        obj = mapper.from_xml(element)

        self.assertEqual('John', obj.father.firstname)
        self.assertEqual('Smith', obj.father.lastname)
        self.assertEqual(52, obj.father.age)

        self.assertEqual('Mary', obj.mother.firstname)
        self.assertEqual('Smith', obj.mother.lastname)
        self.assertEqual(53, obj.mother.age)

        self.assertEqual('Married', obj.status)

    def testfrom_xml4(self):
        text = '''<family xmlns:xmlmapper="xmlmapper">
                    <father>
                        <human age="52" firstname="John" xmlmapper:id="19135952" lastname="Smith">
                            <luckynumbers /><attributes />
                        </human>
                    </father>
                    <mother>
                        <xmlmapper:cache xmlmapper:id="19135952" />
                    </mother>
                    <status>Married</status>
                    <children />
                </family>
        '''
        element = ElementTree.fromstring(text)
        family = mapper.from_xml(element)

        self.assertIs(family.father, family.mother)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

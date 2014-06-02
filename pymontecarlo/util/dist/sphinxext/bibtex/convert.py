#!/usr/bin/env python
"""
================================================================================
:mod:`conversion` -- Conversion utilities
================================================================================

.. module:: conversion
   :synopsis: Conversion utilities

.. inheritance-diagram:: latextools.bibtex.conversion

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

def pybtex_person_to_dict(person):
    return {'first': ' '.join(person.first()),
            'middle': ' '.join(person.middle()),
            'prelast': ' '.join(person.prelast()),
            'last': ' '.join(person.last()),
            'lineage': ' '.join(person.lineage())}

def pybtex_entry_to_dict(entry):
    output = {}

    output['type'] = entry.type
    output.update(entry.fields)

    # Override
    output['keywords'] = entry.fields.get('keywords', '').split(';')
    output['author'] = list(map(pybtex_person_to_dict, entry.persons.get('author', [])))
    output['editor'] = list(map(pybtex_person_to_dict, entry.persons.get('editor', [])))

    return output



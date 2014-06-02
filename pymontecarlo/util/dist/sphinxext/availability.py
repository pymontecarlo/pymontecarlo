#!/usr/bin/env python
"""
================================================================================
:mod:`availability` -- Availability table directive
================================================================================

.. module:: availability
   :synopsis: Availability table directive

.. inheritance-diagram:: pymontecarlo.sphinxext.availability

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter

# Third party modules.
from docutils.parsers.rst.directives.tables import Table
from docutils import nodes
from sphinx import addnodes

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class AvailabilityTableDirective(Table):

    required_arguments = 1
    has_content = False
    option_spec = {'only': str}

    def run(self):
        # Extract choices
        settings = get_settings()
        programs = sorted(settings.get_available_programs(), key=attrgetter('name'))
        attr = self.arguments[0]

        choices = {}
        for program in programs:
            converter = program.converter_class

            for clasz in getattr(converter, attr, []):
                modulepath = clasz.__module__ + '.' + clasz.__name__
                choices.setdefault(modulepath, set()).add(program)

        if 'only' in self.options:
            if self.options['only'] not in choices:
                raise ValueError("Unknown module in only flag")

        # Create table
        table_node = self._build_table(programs, choices)
        table_node['classes'] += self.options.get('class', [])

        self.add_name(table_node)
        return [table_node]

    def _build_table(self, programs, choices):
        env = self.state.document.settings.env
        isonly = 'only' in self.options

        def create_reference(modulepath):
            # From sphinx.roles.XRefRole
            classes = ['xref', 'ref']

            modulename = modulepath.rsplit('.', 1)[-1]
            title = ' '.join(camelcase_to_words(modulename).split()[:-1])
            target = modulename.lower()
            rawtext = ':ref:`%s <%s>`' % (title, target)

            refnode = \
                addnodes.pending_xref(rawtext, reftype='ref', refdomain='std',
                                      refexplicit=True,
                                      reftarget=target,
                                      refdoc=env.docname)
            refnode += nodes.literal(rawtext, title, classes=classes)

            return refnode

        # table
        table = nodes.table()

        ncol = len(programs)
        if not isonly: ncol += 1
        tgroup = nodes.tgroup(cols=ncol)
        table += tgroup

        colwidths = self.get_column_widths(ncol)
        if not isonly: colwidths[0] *= 2
        tgroup.extend(nodes.colspec(colwidth=colwidth) for colwidth in colwidths)

        # header
        thead = nodes.thead()
        tgroup += thead
        rownode = nodes.row()
        thead += rownode
        hs = [''] if not isonly else []
        hs += programs
        rownode.extend(nodes.entry(h, nodes.paragraph(text=h)) for h in hs)

        # body
        tbody = nodes.tbody()
        tgroup += tbody

        for modulepath in sorted(choices):
            available_programs = choices[modulepath]

            if isonly and modulepath != self.options['only']:
                continue

            rownode = nodes.row()
            tbody += rownode

            # Reference to class
            if not isonly:
                refnode = nodes.paragraph()
                refnode += create_reference(modulepath)
                rownode.append(nodes.entry('', refnode))

            # Exist for program
            for program in programs:
                text = 'x' if program in available_programs else ''
                rownode.append(nodes.entry(text, nodes.paragraph(text=text)))


        return table

def setup(app):
    app.add_directive('availability', AvailabilityTableDirective)

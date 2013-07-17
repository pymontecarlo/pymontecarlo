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

# Third party modules.
from docutils.parsers.rst.directives.tables import Table
from docutils import nodes
from sphinx import addnodes
from sphinx.util.nodes import set_role_source_info

# Local modules.
from pymontecarlo.settings import get_settings

# Globals and constants variables.

class AvailabilityTableDirective(Table):

    required_arguments = 1
    has_content = False

    def run(self):
        # Extract choices
        settings = get_settings()
        programs = sorted(settings.get_available_programs())
        attr = self.arguments[0]

        choices = {}
        for program in programs:
            converter = program.converter_class
            
            for clasz in getattr(converter, attr, []):
                modulepath = clasz.__module__ + '.' + clasz.__name__
                choices.setdefault(modulepath, set()).add(program)

        # Create table
        table_node = self._build_table(programs, choices)
        table_node['classes'] += self.options.get('class', [])

        self.add_name(table_node)
        return [table_node]

    def _build_table(self, programs, choices):
        env = self.state.document.settings.env

        def create_api_reference(modulepath):
            # From sphinx.roles.XRefRole
            domain = 'py'
            role = 'class'
            classes = ['xref', role]

            has_explicit_title = True
            title = 'api'
            target = modulepath
            rawtext = ':py:class:`%s <%s>`' % (title, target)

            refnode = \
                addnodes.pending_xref(rawtext, reftype=role, refdomain=domain,
                                      refexplicit=has_explicit_title)
            # we may need the line number for warnings
            set_role_source_info(self.state_machine, self.lineno, refnode)

            refnode['py:module'] = env.temp_data.get('py:module')
            refnode['py:class'] = env.temp_data.get('py:class')

            # now that the target and title are finally determined, set them
            refnode['reftarget'] = target
            refnode += nodes.literal(rawtext, title, classes=classes)
            # we also need the source document
            refnode['refdoc'] = env.docname

            return refnode

        def create_gui_reference(modulepath):
            # From sphinx.roles.XRefRole
            classes = ['xref']
            title = 'gui'
            target = modulepath.rsplit('.', 1)[-1].lower() + '-gui'
            rawtext = ':ref:`%s <%s>`' % (title, target)

            refnode = nodes.reference(refid=target)
            refnode += nodes.literal(rawtext, title, classes=classes)

            return refnode

        # table
        table = nodes.table()

        ncol = len(programs) + 1
        tgroup = nodes.tgroup(cols=ncol)
        table += tgroup

        colwidths = self.get_column_widths(ncol)
        colwidths[0] *= 2
        tgroup.extend(nodes.colspec(colwidth=colwidth) for colwidth in colwidths)

        # header
        thead = nodes.thead()
        tgroup += thead
        rownode = nodes.row()
        thead += rownode
        rownode.extend(nodes.entry(h, nodes.paragraph(text=h))
                       for h in [''] + programs)

        # body
        tbody = nodes.tbody()
        tgroup += tbody
        
        for modulepath, available_programs in choices.iteritems():
            rownode = nodes.row()
            tbody += rownode

            # Reference to class in API and GUI
            classname = modulepath.rsplit('.', 1)[-1]
            guirefnode = create_gui_reference(modulepath)
            apirefnode = create_api_reference(modulepath)

            refnode = nodes.paragraph(classname + ' | ', classname + ' | ')
            refnode += guirefnode
            refnode += nodes.Text(' | ', ' | ')
            refnode += apirefnode
            rownode.append(nodes.entry('', refnode))

            # Exist for program
            for program in programs:
                text = 'x' if program in available_programs else ''
                rownode.append(nodes.entry(text, nodes.paragraph(text=text)))


        return table

def setup(app):
    app.add_directive('availability', AvailabilityTableDirective)

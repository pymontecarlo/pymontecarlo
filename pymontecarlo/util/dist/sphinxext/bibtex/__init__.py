#!/usr/bin/env python
"""
================================================================================
:mod:`bibtex` -- Sphinx extension to use BibTeX references
================================================================================

.. module:: bibtex
   :synopsis: Sphinx extension to use BibTeX references

The following variables must be defined in the ``conf.py``.

  * *bibtex_path*: relative path to the BibTeX file (.bib) from ``conf.py``
  * *bibtex_style*: tuple of the style to use of html and LaTeX
    (e.g. ``('apa', 'apalike')``)
  * *bibtex_styles_path*: list of absolute paths to this extension style
    directories.

To cite a reference, use ``:cite:`Doe2011```, which should refer to a BibTeX
entry with a key *Doe2011*.
To display the bibliography, use the directive ``.. bibliography::``.
It takes no arguments or options.

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os.path

# Third party modules.
from docutils import nodes
from docutils.utils import unescape
from docutils.parsers.rst import Directive
import docutils.parsers.rst.directives as directives

from sphinx.errors import SphinxWarning
from sphinx.util.osutil import SEP, copyfile
from sphinx.util.console import bold #@UnresolvedImport
from sphinx.builders.latex import LaTeXBuilder

from pybtex.database.input.bibtex import Parser as BibtexParser
from pybtex.exceptions import PybtexError

# Local modules.
from pymontecarlo.util.dist.sphinxext.bibtex.style import Style
from pymontecarlo.util.dist.sphinxext.bibtex.convert import pybtex_entry_to_dict
from pymontecarlo.util.dist.sphinxext.bibtex.utils import find_path

# Globals and constants variables.
DEFAULT_STYLE = ('apa', 'apalike')

class bibtex_reference(nodes.Inline, nodes.TextElement):
    pass

class bibtex_bibliography(nodes.Part, nodes.Element):
    pass

def bibtex_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    text = unescape(text)

    env = inliner.document.settings.env

    if not hasattr(env, 'bibtex_refs'):
        env.bibtex_refs = []

    try:
        index = env.bibtex_refs.index(text) + 1
    except ValueError: # new entry
        env.bibtex_refs.append(text)
        index = len(env.bibtex_refs)

    node = bibtex_reference(index, index, target=text)

    return [node], []

#-------------------------------------------------------------------------------

def latex_visit_bibtex_reference(self, node):
    self.body.append('\\citep{%s}' % node['target']) # natbib cite
    raise nodes.SkipNode

def text_visit_bibtex_reference(self, node):
    self.add_text(node['target'])
    raise nodes.SkipNode

def man_visit_bibtex_reference(self, node):
    self.body.append(node['target'])
    raise nodes.SkipNode

def html_visit_bibtex_reference(self, node):
    self.body.append('[<a href="#%s">' % node['target'])

def html_depart_bibtex_reference(self, node):
    self.body.append('</a>]')

#-------------------------------------------------------------------------------

def html_visit_bibtex_bibliography(self, node):
    self.body.append('<hr/>')

def html_depart_bibtex_bibliography(self, node):
    pass

def latex_visit_bibtex_bibliography(self, node):
    raise nodes.SkipNode

def text_visit_bibtex_bibliography(self, node):
    raise nodes.SkipNode

def man_visit_bibtex_bibliography(self, node):
    raise nodes.SkipNode

#-------------------------------------------------------------------------------

class BibtexDirective(Directive):
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        if not hasattr(env, 'bibtex_refs'):
            return [bibtex_bibliography()]

#        print dir(env)
#        print env.doc2path(env.docname)

        bibtex_refs = env.bibtex_refs
        env.bibtex_refs = []
        entries = env.bibtex_entries
        style = Style(env.bibtex_style_dir, env.bibtex_style_name)

        list_node = nodes.enumerated_list()
        list_node['classes'].append('bibliography')

        for ref in bibtex_refs:
            if ref not in entries:
                raise self.warning("%s: reference not found." % ref)

            entry = entries[ref]
            rendered = style.render(pybtex_entry_to_dict(entry))
            if not rendered:
                raise self.warning("%s: no template for entry type (%s)." % \
                                   (ref, entry.type))

            list_item = nodes.list_item()
            list_item['ids'].append(ref)
            list_item += nodes.raw(rendered, rendered, format="html")

            list_node += list_item

        bibliography = bibtex_bibliography()
        bibliography += list_node

        return [bibliography]

#-------------------------------------------------------------------------------

def parse_bibtex(app):
    # load bibtex path
    if not app.config.bibtex_path:
        raise SphinxWarning('No BibTeX path specified.')

    if os.path.isabs(app.config.bibtex_path):
        filepath = app.config.bibtex_path
    else:
        filepath = os.path.join(app.confdir, app.config.bibtex_path)

    if not os.path.exists(filepath):
        raise SphinxWarning("BibTeX file (%s) does not exists." % filepath)

    app.env.bibtex_path = filepath

    # parse bib
    parser = BibtexParser()

    try:
        data = parser.parse_file(filepath)
    except PybtexError as ex:
        raise SphinxWarning(ex)

    app.env.bibtex_entries = data.entries

    # latex reconfiguration
    filename = os.path.splitext(os.path.basename(filepath))[0]
    app.config.latex_elements.setdefault('footer', '')
    app.config.latex_elements['footer'] += "\\bibliography{%s}" % filename

def load_style_dir(app):
    if not app.config.bibtex_styles_path:
        raise SphinxWarning('No BibTeX styles path specified.')

    styles_paths = app.config.bibtex_styles_path
    if isinstance(styles_paths, str):
        styles_paths = [styles_paths]

    html_style_name, latex_style_name = app.config.bibtex_style
    style_dir = None

    for path in styles_paths:
        dirpath = os.path.join(path, html_style_name + '.html')
        if os.path.exists(dirpath):
            style_dir = path

    if not style_dir:
        raise SphinxWarning("Style (%s) does not exist in the styles path." % \
                            html_style_name)

    # NOTE: Store style dir and not style in env since Style class cannot be pickle
    app.env.bibtex_style_dir = style_dir
    app.env.bibtex_style_name = html_style_name

    # latex reconfiguration
    app.config.latex_elements.setdefault('preamble', '')
    app.config.latex_elements['preamble'] += '\\usepackage{natbib}'

    app.config.latex_elements.setdefault('footer', '')
    app.config.latex_elements['footer'] += "\\bibliographystyle{%s}" % latex_style_name

def finish_latex(app, exception):
    if exception is None and app.env.bibtex_path and \
            isinstance(app.builder, LaTeXBuilder):
        app.info(bold("copying BibTeX file..."), nonl=1)

        src = app.env.bibtex_path
        dst = os.path.join(app.builder.outdir, os.path.basename(src))
        copyfile(src, dst)

        app.info('done')

#-------------------------------------------------------------------------------

def setup(app):
    app.add_config_value('bibtex_styles_path', [], False)
    app.add_config_value('bibtex_style', DEFAULT_STYLE, False)
    app.add_config_value('bibtex_path', None, False)

    app.add_node(bibtex_bibliography,
                 html=(html_visit_bibtex_bibliography, html_depart_bibtex_bibliography),
                 latex=(latex_visit_bibtex_bibliography, None),
                 text=(text_visit_bibtex_bibliography, None),
                 man=(man_visit_bibtex_bibliography, None))
    app.add_node(bibtex_reference,
                 latex=(latex_visit_bibtex_reference, None),
                 text=(text_visit_bibtex_reference, None),
                 man=(man_visit_bibtex_reference, None),
                 html=(html_visit_bibtex_reference, html_depart_bibtex_reference))

    app.add_role('cite', bibtex_role)

    app.add_directive('bibliography', BibtexDirective)

    app.connect('builder-inited', parse_bibtex)
    app.connect('builder-inited', load_style_dir)
    app.connect('build-finished', finish_latex)

def setup_module():
    # Hack for nosetests
    # From: http://stackoverflow.com/questions/23749154/disable-nose-running-setup
    pass
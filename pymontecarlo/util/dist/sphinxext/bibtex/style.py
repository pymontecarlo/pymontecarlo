#!/usr/bin/env python
"""
================================================================================
:mod:`style` -- Interface between the BibTeX entries and style templates
================================================================================

.. module:: style
   :synopsis: Interface between the BibTeX entries and style templates

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from jinja2 import Environment, FileSystemLoader

# Local modules.
from pymontecarlo.util.dist.sphinxext.bibtex.filters import \
    abbrev, title_case, sentence_case, caps, remove_empty

# Globals and constants variables.

class Style(object):
    def __init__(self, style_dir, style):
        env = Environment(loader=FileSystemLoader(style_dir))
        env.filters['abbrev'] = abbrev
        env.filters['title_case'] = title_case
        env.filters['sentence_case'] = sentence_case
        env.filters['caps'] = caps
        env.filters['remove_empty'] = remove_empty

        self._template = env.get_template(style + ".html")

    def render(self, entry):
        kwargs = self._build_kwargs(entry)
        return self._template.render(**kwargs)

    def _build_kwargs(self, entry):
        kwargs = {}

        kwargs.update(entry)
        kwargs['pages'] = self._format_pages(entry) # overwrite pages

        return kwargs

    def _format_pages(self, entry):
        oldpages = entry.get('pages', '')
        newpages = []

        for part in oldpages.split(','):
            if "--" in part:
                newpages.append(tuple(part.split('--')))
            else:
                newpages.append((part,))

        return newpages


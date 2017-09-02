""""""

# Standard library modules.

# Third party modules.
import docutils.core

# Local modules.

# Globals and constants variables.

def publish_html(builder):
    document = builder.build()
    return docutils.core.publish_from_doctree(document, writer_name='html5')

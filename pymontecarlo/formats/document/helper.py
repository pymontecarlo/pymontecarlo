""""""

# Standard library modules.

# Third party modules.
import docutils.core

# Local modules.

# Globals and constants variables.

def publish_html(builder):
    document = builder.build()
    return docutils.core.publish_from_doctree(document, writer_name='html5')

def count_document_nodes(document):
    def recursive(node, total=0):
        if not hasattr(node, 'children'):
            return total

        total += len(node.children)
        for childnode in node:
            return recursive(childnode, total)

        return total

    return recursive(document)
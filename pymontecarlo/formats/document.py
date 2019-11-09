""""""

# Standard library modules.
from collections import OrderedDict  # @UnresolvedImport

# Third party modules.
import docutils.core
import docutils.nodes
import docutils.utils

# Local modules.
from pymontecarlo.formats.base import FormatBuilderBase

# Globals and constants variables.


class DocutilsFormatBuilderBase(FormatBuilderBase):
    def _format_value_node(self, datum, node_class=None):
        if node_class is None:
            node_class = docutils.nodes.paragraph

        value = datum["value"]
        if isinstance(value, docutils.nodes.Node):
            if type(value) is node_class:
                return value
            else:
                node = node_class()
                node += value
                return node

        return node_class(text=super()._format_value(datum))


class DocumentBuilder(DocutilsFormatBuilderBase):
    def __init__(self, settings):
        super().__init__(settings, abbreviate_name=False, format_number=True)
        self.nodes = []
        self.description_builders = {}
        self.bullet_builders = {}
        self.table_builders = {}

    def add_title(self, title):
        node = docutils.nodes.title(text=title)
        self.nodes.append(node)

    def add_subtitle(self, subtitle):
        node = docutils.nodes.subtitle(text=subtitle)
        self.nodes.append(node)

    def add_entity(self, entity):
        entity.convert_document(self)

    def add_section(self):
        builder = self.__class__(self.settings)
        self.nodes.append(builder)
        return builder

    def add_text(self, text):
        node = docutils.nodes.paragraph(text=text)
        self.nodes.append(node)

    def require_description(self, identifier):
        if identifier in self.description_builders:
            return self.description_builders[identifier]

        builder = DescriptionBuilder(self.settings)
        self.description_builders[identifier] = builder
        self.nodes.append(builder)
        return builder

    def require_bullet(self, identifier):
        if identifier in self.bullet_builders:
            return self.bullet_builders[identifier]

        builder = BulletBuilder(self.settings)
        self.bullet_builders[identifier] = builder
        self.nodes.append(builder)
        return builder

    def require_table(self, identifier):
        if identifier in self.table_builders:
            return self.table_builders[identifier]

        builder = TableBuilder(self.settings)
        self.table_builders[identifier] = builder
        self.nodes.append(builder)
        return builder

    def build(self):
        document = docutils.utils.new_document("")

        section = docutils.nodes.section()
        document += section

        for node in self.nodes:
            if isinstance(node, FormatBuilderBase):
                section += node.build().children
            elif isinstance(node, docutils.nodes.Node):
                section += node

        return document


class DescriptionBuilder(DocutilsFormatBuilderBase):
    def __init__(self, settings):
        super().__init__(settings, abbreviate_name=False, format_number=True)
        self.data = []

    def add_item(self, name, value, unit=None, tolerance=None):
        datum = self._create_datum(name, name, value, unit, tolerance)
        self.data.append(datum)

    def build(self):
        definition_list = docutils.nodes.definition_list()

        for datum in self.data:
            term = docutils.nodes.term(text=self._format_label(datum))

            definition = docutils.nodes.definition()
            definition += self._format_value_node(datum)

            definition_item = docutils.nodes.definition_list_item()
            definition_item += term
            definition_item += definition

            definition_list += definition_item

        document = docutils.utils.new_document("")
        document += definition_list
        return document


class BulletBuilder(DocutilsFormatBuilderBase):
    def __init__(self, settings):
        super().__init__(settings, abbreviate_name=False, format_number=True)
        self.data = []

    def add_item(self, value, unit=None, tolerance=None):
        datum = self._create_datum("untitled", "untitled", value, unit, tolerance)
        self.data.append(datum)

    def build(self):
        bullet_list = docutils.nodes.bullet_list()

        for datum in self.data:
            item = docutils.nodes.list_item()
            item += self._format_value_node(datum)
            bullet_list += item

        document = docutils.utils.new_document("")
        document += bullet_list
        return document


class TableBuilder(DocutilsFormatBuilderBase):
    def __init__(self, settings):
        super().__init__(settings, abbreviate_name=False, format_number=True)
        self.columns = OrderedDict()
        self.rows = []

    def add_column(self, name, unit=None, tolerance=None):
        if name in self.columns:
            return

        datum = self._create_datum(name, name, None, unit, tolerance)
        self.columns[name] = datum

    def add_row(self, row):
        """
        Add a row.
        
        Args:
            row (dict): a dictionary where the keys are the column names,
                and the values are the values for each cell
        """
        self.rows.append(row)

    def build(self):
        table = docutils.nodes.table()

        # Group
        tgroup = docutils.nodes.tgroup(cols=len(self.columns))
        table += tgroup

        for datum in self.columns.values():
            colspec = docutils.nodes.colspec(colwidth=1)
            tgroup += colspec

        # Head
        thead = docutils.nodes.thead()
        tgroup += thead

        headrow = docutils.nodes.row()
        thead += headrow

        for datum in self.columns.values():
            label = self._format_label(datum)
            paragraph = docutils.nodes.paragraph(text=label)

            entry = docutils.nodes.entry()
            entry += paragraph
            headrow += entry

        # Body
        tbody = docutils.nodes.tbody()
        tgroup += tbody

        for row in self.rows:
            if not isinstance(row, dict):
                row = dict(zip(self.columns.keys(), row))

            trow = docutils.nodes.row()
            tbody += trow

            for name, datum in self.columns.items():
                datum = datum.copy()
                datum["value"] = row.get(name, "")
                paragraph = self._format_value_node(datum)

                entry = docutils.nodes.entry()
                entry += paragraph
                trow += entry

        # Document
        document = docutils.utils.new_document("")
        document += table
        return document


def publish_html(builder):
    document = builder.build()
    return docutils.core.publish_from_doctree(document, writer_name="html5")

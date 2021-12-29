""""""

# Standard library modules.
import re
import importlib

# Third party modules.
import docutils.nodes
from docutils.parsers.rst import Directive

# Local modules.

# Globals and constants variables.


def split_camelcase(text):
    matches = re.finditer(".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", text)
    return [m.group(0) for m in matches]


class SupportedOptionsDirective(Directive):

    # this enables content in the directive
    has_content = True

    required_arguments = 1

    def _parse_programs(self):
        env = self.state.document.settings.env
        entrypoints = env.config.pymontecarlo_programs

        programs = []
        for entrypoint in entrypoints:
            package, classname = entrypoint.split(":")
            module = importlib.import_module(package)
            clasz = getattr(module, classname)
            programs.append(clasz())

        # Add mock validator
        module = importlib.import_module("pymontecarlo.mock")
        clasz = getattr(module, "ProgramMock")
        programs.append(clasz())

        return programs

    def _collect_options(self, programs, option_type):
        if option_type == "beam":
            method_name = "beam_export_methods"
        elif option_type == "sample":
            method_name = "sample_export_methods"
        elif option_type == "analysis":
            method_name = "analysis_export_methods"
        else:
            return {}

        options = {}
        for program in programs:
            program_name = program.name

            exporter = program.exporter

            for clasz in getattr(exporter, method_name):
                class_name = " ".join(split_camelcase(clasz.__name__)[:-1])
                class_name = class_name.capitalize()
                options.setdefault(program_name, []).append(class_name)

        return options

    def run(self):
        programs = self._parse_programs()
        option_type = self.arguments[0].lower()

        # Collection options
        options = self._collect_options(programs, option_type)

        # Define columns
        all_options = set()
        for names in options.values():
            all_options.update(names)
        all_options = sorted(all_options)

        # Create table
        table = docutils.nodes.table()

        tgroup = docutils.nodes.tgroup(cols=len(all_options) + 1)
        table += tgroup

        colspec = docutils.nodes.colspec(colwidth=1.25)
        tgroup += colspec

        for _ in range(len(all_options)):
            colspec = docutils.nodes.colspec(colwidth=1, align="center")
            tgroup += colspec

        # Head
        thead = docutils.nodes.thead()
        tgroup += thead

        headrow = docutils.nodes.row()
        thead += headrow

        entry = docutils.nodes.entry()
        headrow += entry

        for option_name in all_options:
            paragraph = docutils.nodes.paragraph(text=option_name)
            entry = docutils.nodes.entry()
            entry += paragraph
            headrow += entry

        # Body
        tbody = docutils.nodes.tbody()
        tgroup += tbody

        for program_name in sorted(options):
            if program_name == "mock":
                continue

            trow = docutils.nodes.row()
            tbody += trow

            paragraph = docutils.nodes.paragraph(text=program_name)
            entry = docutils.nodes.entry()
            entry += paragraph
            trow += entry

            for option_name in all_options:
                text = "x" if option_name in options[program_name] else ""
                paragraph = docutils.nodes.paragraph(text=text)
                entry = docutils.nodes.entry()
                entry += paragraph
                trow += entry

        return [table]


def setup(app):
    app.add_config_value("pymontecarlo_programs", [], "env")

    app.add_directive("supported-options", SupportedOptionsDirective)

    return {"version": "0.1"}  # identifies the version of our extension

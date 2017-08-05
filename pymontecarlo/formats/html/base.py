""""""

# Standard library modules.
import abc

# Third party modules.
import dominate.tags as tags
from dominate.util import raw

# Local modules.
from pymontecarlo.exceptions import ConvertError
from pymontecarlo.util.entrypoint import resolve_entrypoints, ENTRYPOINT_HTMLHANDLER
from pymontecarlo.util.tolerance import tolerance_to_decimals

# Globals and constants variables.

def find_convert_htmlhandler(obj):
    for entrypoint in resolve_entrypoints(ENTRYPOINT_HTMLHANDLER).values():
        clasz = entrypoint.resolve()
        handler = clasz()
        if handler.can_convert(obj):
            return handler
    raise ConvertError("No handler found for object {!r}".format(obj))

class HtmlHandler(object, metaclass=abc.ABCMeta):

    def _find_and_convert(self, obj, settings, level=1):
        return find_convert_htmlhandler(obj).convert(obj, settings, level)

    def _format_value(self, settings, value, unit=None, tolerance=None):
        precision = None
        if tolerance is not None:
            if unit is not None:
                q_tolerance = settings.to_preferred_unit(tolerance, unit)
                tolerance = q_tolerance.magnitude
            precision = tolerance_to_decimals(tolerance)

        if unit is not None:
            q = settings.to_preferred_unit(value, unit)
            value = q.magnitude

        if isinstance(value, float):
            if precision is not None:
                return '{0:.{precision}f}'.format(value, precision=precision)
            else:
                return '{:g}'.format(value)

        return '{}'.format(value)

    def _create_label(self, settings, label, unit=None):
        if unit is not None:
            q = settings.to_preferred_unit(1.0, unit)
            unit = q.units

            unitname = '{:~H}'.format(unit)
            if not unitname: # required for radian and degree
                unitname = '{:H}'.format(unit)

            label = '{} [{}]'.format(label, unitname)

        return label

    def _create_header(self, level, text):
        clasz = getattr(tags, 'h{:d}'.format(level))
        return clasz(text)

    def _create_description(self, settings, label, value, unit=None, tolerance=None):
        label = self._create_label(settings, label, unit)
        dt = tags.dt(raw(label))

        value = self._format_value(settings, value, unit, tolerance)
        dd = tags.dd(value)

        return [dt, dd]

    def _create_table(self, rows):
        columns = []
        for row in rows:
            for column in row.keys():
                if column in columns:
                    continue
                columns.append(column)

        # Create table
        table = tags.table()

        thead = tags.thead()
        tr = tags.tr()
        for column in columns:
            tr += tags.th(raw(column))
        thead += tr

        tbody = tags.tbody()
        for row in rows:
            tr = tags.tr()
            for column in columns:
                tr += tags.td(row.get(column, ''))
            tbody += tr

        table += thead
        table += tbody

        return table

    def _create_table_objects(self, objs, settings):
        # Accumulate rows
        rows = []
        for obj in objs:
            handler = find_convert_htmlhandler(obj)
            rows.extend(handler.convert_rows(obj, settings))

        return self._create_table(rows)

    def can_convert(self, obj):
        return type(obj) is self.CLASS

    @abc.abstractmethod
    def convert(self, obj, settings, level=1):
        return tags.html_tag()

    @abc.abstractproperty
    def CLASS(self):
        raise NotImplementedError

    @property
    def VERSION(self):
        return 1

class TableHtmlHandler(HtmlHandler):

    @abc.abstractmethod
    def convert_rows(self, obj, settings):
        return []

    def convert(self, obj, settings, level=1):
        root = super().convert(obj, settings, level)
        root += self._create_table_objects([obj], settings)
        return root

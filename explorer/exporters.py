from django.db import DatabaseError
import json
import string
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import sys
PY3 = sys.version_info[0] == 3
if PY3:
    import csv
else:
    import unicodecsv as csv

from django.utils.module_loading import import_string

from . import app_settings


def get_exporter_class(format):
    class_str = getattr(app_settings, 'EXPLORER_DATA_EXPORTERS')[format]
    return import_string(class_str)


class BaseExporter(object):

    name = ''
    content_type = ''
    file_extension = ''

    def __init__(self, query):
        self.query = query

    def get_output(self, **kwargs):
        try:
            res = self.query.execute_query_only()
            return self._get_output(res, **kwargs)
        except DatabaseError as e:
            resp = StringIO.StringIO()
            return resp.write(str(e))  # consistent return type

    def _get_output(self, **kwargs):
        raise NotImplementedError

    def get_filename(self):
        # build list of valid chars, build filename from title and replace spaces
        valid_chars = '-_.() %s%s' % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in self.query.title if c in valid_chars)
        filename = filename.replace(' ', '_')
        return '{}{}'.format(filename, self.file_extension)


class CSVExporter(BaseExporter):

    name = 'CSV'
    content_type = 'text/csv'
    file_extension = '.csv'

    def _get_output(self, res, **kwargs):
        delim = kwargs.get('delim') or app_settings.CSV_DELIMETER
        delim = '\t' if delim == 'tab' else str(delim)
        delim = app_settings.CSV_DELIMETER if len(delim) > 1 else delim
        csv_data = StringIO.StringIO()
        if PY3:
            writer = csv.writer(csv_data, delimiter=delim)
        else:
            writer = csv.writer(csv_data, delimiter=delim, encoding='utf-8')
        writer.writerow(res.headers)
        for row in res.data:
            writer.writerow([s for s in row])
        return csv_data.getvalue()


class JSONExporter(BaseExporter):

    name = 'JSON'
    content_type = 'application/json'
    file_extension = '.json'

    def _get_output(self, res, **kwargs):
        data = []
        for row in res.data:
            data.append(
                dict(zip([str(h) if h is not None else '' for h in res.headers], row))
            )

        json_data = json.dumps(data)
        return json_data


class ExcelExporter(BaseExporter):

    name = 'Excel'
    content_type = 'application/vnd.ms-excel'
    file_extension = '.xls'

    def _get_output(self, res, **kwargs):
        import xlwt

        wb = xlwt.Workbook()
        ws = wb.add_sheet(self.query.title)

        # Write headers
        row = 0
        col = 0
        header_style = xlwt.easyxf('font: bold on; borders: bottom thin')
        for header in res.headers:
            ws.write(row, col, str(header), header_style)
            col += 1

        # Write data
        row = 1
        col = 0
        for data_row in res.data:
            for data in data_row:
                ws.write(row, col, data)
                col += 1
            row += 1
            col = 0

        output = StringIO.StringIO()
        wb.save(output)
        return output.getvalue()

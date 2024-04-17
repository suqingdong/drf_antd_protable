import io
import datetime
from pathlib import Path
from uuid import UUID

import unicodecsv
import openpyxl

from django.http import FileResponse
from wsgiref.util import FileWrapper

from rest_framework.response import Response


def safe_open(filename, mode='r'):
    file = Path(filename)

    if 'w' in mode and not file.parent.exists():
        file.parent.mkdir(parents=True)

    if filename.endswith('.gz'):
        import gzip
        return gzip.open(filename, mode=mode)

    return file.open(mode=mode)


class Exporter(object):

    def __init__(self, data, title_map=None, savefile=None):
        self.data = data
        self.title_map = title_map or {}
        self.buffer = safe_open(savefile, 'wb') if savefile else io.BytesIO()

    def export(self, exportType, filename=None):

        if exportType == 'csv':
            return self._to_csv(filename or 'Export.csv')
        elif exportType == 'xlsx':
            return self._to_excel(filename or 'Export.xlsx')
        else:
            return Response('exportType not supported!')
        

    @staticmethod
    def check_values(values):
        for value in values:
            if isinstance(value, list):
                value = ','.join(map(str, value))
            elif isinstance(value, dict):
                if value.get('$date'):
                    value = datetime.date.fromtimestamp(value.get('$date') / 1000).strftime('%F')
                else:
                    value = str(value)
            elif isinstance(value, datetime.datetime):
                value = value.strftime('%F')
            elif isinstance(value, UUID):
                value = str(value)
            else:
                value = str(value)
            yield value

    def _to_excel(self, filename):
        buffer = io.BytesIO()
        wb = openpyxl.Workbook()
        ws = wb.active

        for n, row in enumerate(self.data):
            if n == 0:
                title = [self.title_map.get(t, t) for t in row.keys()]
                ws.append(title)
            ws.append(list(self.check_values(row.values())))

        wb.save(self.buffer)
        self.buffer.seek(0)

        return FileResponse(self.buffer, as_attachment=True, content_type='application/ms-excel', filename=filename)

    def _to_csv(self, filename):
        writer = unicodecsv.writer(self.buffer, encoding='utf-8-sig')
        for n, row in enumerate(self.data):
            if n == 0:
                title = [self.title_map.get(t, t) for t in row.keys()]
                writer.writerow(title)
            writer.writerow(list(self.check_values(row.values())))

        self.buffer.seek(0)

        return FileResponse(self.buffer, as_attachment=True, content_type='text/csv', filename=filename)

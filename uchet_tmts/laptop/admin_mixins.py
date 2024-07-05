import csv
import codecs
from dataclasses import field
from urllib import response

from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from django.db.models.options import Options


class ExportAsCSVMixin:
    def export_csv(self, request: HttpRequest, queryset: QuerySet):
        meta: Options = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}-export.csv'

        response.write(codecs.BOM_UTF8) #  Экспорт в UTF-8

        csv_writer = csv.writer(response, delimiter = ";")
        
        csv_writer.writerow(field_names)

        for obj in queryset:
            csv_writer.writerow([getattr(obj, field) for field in field_names])

        return response
    
    export_csv.short_description = 'Export as CSV'

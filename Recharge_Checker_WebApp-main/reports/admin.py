from django.contrib import admin

from .models import Renewal, ReportMeta, Snapshot

admin.site.register(Renewal)
admin.site.register(ReportMeta)
admin.site.register(Snapshot)

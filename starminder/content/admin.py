from django.contrib import admin

from starminder.content.models import Entry, Reminder

admin.site.register(Reminder)
admin.site.register(Entry)

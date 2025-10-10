from django.contrib import admin

from starminder.content.models import Entry, Post

admin.site.register(Post)
admin.site.register(Entry)

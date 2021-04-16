from django.contrib import admin
from .models import Song, SongFingerprint

# Register your models here.
admin.site.register((Song, SongFingerprint))
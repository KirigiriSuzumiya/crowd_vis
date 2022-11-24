from django.contrib import admin

# Register your models here.
from .models import crowdinfo, warning

admin.site.register(crowdinfo)
admin.site.register(warning)

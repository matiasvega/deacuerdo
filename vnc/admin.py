from django.apps import apps
from django.contrib import admin
from django.forms import NumberInput
from django.db import models


class YourModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.IntegerField: {'widget': NumberInput(attrs={'size': '34'})},
        models.BigIntegerField: {'widget': NumberInput(attrs={'size': '34'})}
    }


for model in apps.get_app_config('vnc').get_models():
    admin.site.register(model, YourModelAdmin)

from django.contrib import admin
from apps.store.models import Store, Flavor

# Register your models here.
admin.site.register(Store)
admin.site.register(Flavor)

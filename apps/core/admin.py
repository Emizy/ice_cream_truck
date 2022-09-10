from django.contrib import admin
from apps.core.models import User, Company, Franchise, IceCreamTruck


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "mobile",
        "date_joined",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Franchise)
admin.site.register(IceCreamTruck)

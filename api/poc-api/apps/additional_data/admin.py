
from django.contrib import admin

from apps.additional_data.models import (
    Village, Destination, Parcel, TreeSpecie, OvenType
)


admin.site.register(Village)
admin.site.register(Destination)
admin.site.register(Parcel)
admin.site.register(TreeSpecie)
admin.site.register(OvenType)

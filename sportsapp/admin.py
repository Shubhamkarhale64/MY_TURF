from django.contrib import admin
from .models import Sport


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'name',
    )

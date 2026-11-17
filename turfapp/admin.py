
from django.contrib import admin
from .models import Turf, TurfOwner, TurfSport, Slot, Booking


@admin.register(TurfOwner)
class TurfOwnerAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "user",
        "get_email",
        "verification_status",
        "created_at",
    )

    list_filter = ("verification_status",)
    search_fields = (
        "business_name",
        "user__username",
        "user__email",
    )

    @admin.display(description="Email")
    def get_email(self, obj):
        return obj.user.email


@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "city",
        "area",
        "price_per_hour",
        "status",
        "rating",
    )

    list_filter = ("status", "city", "ground_type")
    search_fields = ("name", "city", "area", "address")

    actions = (
        "approve_turfs",
        "reject_turfs",
    )

    @admin.action(description="Approve selected turfs")
    def approve_turfs(self, request, queryset):
        updated = queryset.update(status="APPROVED")
        self.message_user(request, f"{updated} turf(s) approved.")

    @admin.action(description="Reject selected turfs")
    def reject_turfs(self, request, queryset):
        updated = queryset.update(status="REJECTED")
        self.message_user(request, f"{updated} turf(s) rejected.")


@admin.register(TurfSport)
class TurfSportAdmin(admin.ModelAdmin):
    list_display = ("turf", "sport")
    list_filter = ("sport",)
    search_fields = ("turf__name", "sport__name")


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = (
        "turf",
        "date",
        "start_time",
        "end_time",
        "price",
        "status",
    )

    list_filter = ("status", "date", "turf")
    search_fields = ("turf__name",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_code",
        "user",
        "turf",
        "slot",
        "booking_date",
        "amount",
        "booking_status",
        "payment_status",
        "created_at",
    )

    list_filter = (
        "booking_status",
        "payment_status",
        "booking_date",
    )

    search_fields = (
        "booking_code",
        "user__username",
        "turf__name",
    )

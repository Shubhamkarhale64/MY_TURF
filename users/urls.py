
from django.urls import path
from .views import (
    owner_register,
    owner_login,
    owner_dashboard,
    my_turfs,
    add_turf,
    edit_turf,
    manage_slots,
    delete_slot,
    edit_slot,
    turf_search,
    turf_detail,
    turf_slots,
    book_slot,
    customer_register,
    customer_login,
    customer_logout,
    customer_profile,
    booking_summary,
    payment,
    my_bookings,
    cancel_booking,
    owner_bookings,
    owner_cancel_booking
)

urlpatterns = [
    # Customer authentication
    path("register/", customer_register, name="customer_register"),
    path("login/", customer_login, name="customer_login"),
    path("logout/", customer_logout, name="customer_logout"),
    path("profile/", customer_profile, name="customer_profile"),

    # Owner authentication and dashboard
    path("owner/login/", owner_login, name="owner_login"),
    path("owner/dashboard/", owner_dashboard, name="owner_dashboard"),
    path("owner/my-turfs/", my_turfs, name="my_turfs"),
    path("owner/add-turf/", add_turf, name="add_turf"),
    path(
        "owner/edit-turf/<int:turf_id>/",
        edit_turf,
        name="edit_turf",
    ),

    # Slot management
    path("owner/manage-slots/", manage_slots, name="manage_slots"),
    path(
        "owner/delete-slot/<int:slot_id>/",
        delete_slot,
        name="delete_slot",
    ),
    path(
        "owner/edit-slot/<int:slot_id>/",
        edit_slot,
        name="edit_slot",
    ),

    # Turf search and details
    path("turfs/", turf_search, name="turf_search"),
    path(
        "turfs/<int:turf_id>/",
        turf_detail,
        name="turf_detail",
    ),
    path(
        "turfs/<int:turf_id>/slots/",
        turf_slots,
        name="turf_slots",
    ),

    # Booking
    path(
        "book-slot/<int:slot_id>/",
        book_slot,
        name="book_slot",
    ),
    path(
        "booking-summary/<int:booking_id>/",
        booking_summary,
        name="booking_summary",
    ),
    path(
        "my-bookings/",
        my_bookings,
        name="my_bookings",
    ),
    path(
        "cancel-booking/<int:booking_id>/",
        cancel_booking,
        name="cancel_booking",
    ),

    # Payment
    path(
        "payment/<int:booking_id>/",
        payment,
        name="payment",
    ),
    path("owner/register/", owner_register, name="owner_register"),
    path("owner/bookings/", owner_bookings, name="owner_bookings"),
    path(
    "owner/cancel-booking/<int:booking_id>/",
    owner_cancel_booking,
    name="owner_cancel_booking",
),
]


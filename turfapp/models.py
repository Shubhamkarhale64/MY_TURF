
from django.db import models
from django.contrib.auth.models import User


class TurfOwner(models.Model):
    VERIFICATION_CHOICES = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="turf_owner",
    )

    business_name = models.CharField(max_length=150)

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default="PENDING",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name


class Turf(models.Model):
    STATUS_CHOICES = [
        ("PENDING_APPROVAL", "Pending Approval"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("INACTIVE", "Inactive"),
    ]

    owner = models.ForeignKey(
        TurfOwner,
        on_delete=models.CASCADE,
        related_name="turfs",
    )

    name = models.CharField(max_length=150)

    image = models.ImageField(
        upload_to="turf_images/",
        null=True,
        blank=True,
    )

    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    ground_type = models.CharField(
        max_length=100,
        blank=True,
    )

    open_time = models.TimeField(
        null=True,
        blank=True,
    )

    close_time = models.TimeField(
        null=True,
        blank=True,
    )

    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING_APPROVAL",
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Slot(models.Model):
    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("BOOKED", "Booked"),
        ("BLOCKED", "Blocked"),
    ]

    turf = models.ForeignKey(
        Turf,
        on_delete=models.CASCADE,
        related_name="slots",
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AVAILABLE",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.turf.name} - "
            f"{self.date} - {self.start_time}"
        )


class TurfSport(models.Model):
    turf = models.ForeignKey(
        Turf,
        on_delete=models.CASCADE,
        related_name="turf_sports",
    )

    sport = models.ForeignKey(
        "sportsapp.Sport",
        on_delete=models.CASCADE,
        related_name="turf_sports",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["turf", "sport"],
                name="unique_turf_sport",
            )
        ]

    def __str__(self):
        return f"{self.turf.name} - {self.sport.name}"


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    booking_code = models.CharField(
        max_length=20,
        unique=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    turf = models.ForeignKey(
        Turf,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    slot = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    booking_date = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    booking_status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default="PENDING",
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.booking_code

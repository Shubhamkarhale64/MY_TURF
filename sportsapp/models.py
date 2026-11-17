
from django.db import models


class Sport(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    icon = models.CharField(
        max_length=255,
        blank=True
    )

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

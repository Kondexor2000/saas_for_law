from django.conf import settings
from django.db import models

class Case(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Nowa"
        ASSIGNED = "assigned", "Przypisana"
        IN_PROGRESS = "in_progress", "W toku"
        CLOSED = "closed", "Zamknięta"

    client = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="submitted_cases")
    lawyer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="assigned_cases")
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    client_phone = models.CharField(max_length=32)
    client_email = models.EmailField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

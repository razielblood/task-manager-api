from django.db import models


# Create your models here.
class Task(models.Model):
    STATE_CHOICES = (
        ("C", "Created"),
        ("P", "In Progress"),
        ("D", "Done"),
    )

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)
    due_date = models.DateField()
    state = models.CharField(max_length=1, choices=STATE_CHOICES)

    class Meta:
        ordering = ("due_date",)

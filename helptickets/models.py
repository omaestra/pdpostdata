from django.db import models
from django.contrib.auth.models import User


STATUS_CHOICES = (
    ("Abierto", "Abierto"),
    ("Cerrado", "Cerrado"),
)


class HelpTicket(models.Model):
    user = models.ForeignKey(User)
    help_ticket_id = models.CharField(max_length=120, default='ABC', unique=True)
    subject = models.CharField(max_length=50, blank=False, null=False)
    message = models.TextField(max_length=200, blank=False, null=False)
    status = models.CharField(max_length=120, choices=STATUS_CHOICES, default="Abierto")
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

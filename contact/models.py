from django.db import models

class Contact(models.Model):
    """Model to send a contact message"""
    name = models.CharField(max_length=40, null=False, blank=False)
    email = models.EmailField(max_length=100, null=False, blank=False)
    subject = models.CharField(max_length=50, null=False, blank=False)
    message = models.TextField(max_length=1000, null=False, blank=False)

    def __str__(self):
        return self.subject
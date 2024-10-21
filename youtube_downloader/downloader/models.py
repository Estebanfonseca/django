from django.db import models

class Download(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

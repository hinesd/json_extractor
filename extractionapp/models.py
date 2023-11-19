from django.db import models

class UrlState(models.Model):
    url = models.URLField()
    time_fetched = models.DateTimeField()
    fetch_status = models.IntegerField(max_length=10, null=True, blank=True)
    raw_content = models.TextField(null=True, blank=True)
    extracted_content = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ['url', 'time_fetched']
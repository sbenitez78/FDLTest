from django.db import models

class CSVImporter(models.Model):
   
    csv_id = models.IntegerField(null=True, blank=True)  # ID del CSV  #not needed ID,
    name = models.CharField(max_length=255)
    year = models.CharField(max_length=50, blank=True)
    tv_certificate = models.CharField(max_length=10, blank=True)
    duration_per_episode = models.CharField(max_length=20, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    rating = models.FloatField(null=True, blank=True)
    actors = models.TextField(blank=True)
    votes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

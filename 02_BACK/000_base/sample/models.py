from django.db import models

# Create your models here.
class Sample(models.Model):
    title = models.CharField(max_length=60)
    content = models.CharField(max_length=500)

    def __str__(self):
        return self.title
from django.db import models

# Create your models here.
class Document(models.Model):
    myfilefield = models.FileField(upload_to='documents/')
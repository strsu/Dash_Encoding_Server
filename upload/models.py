from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=100)
    file  = models.FileField(
                upload_to='./media/raw/', 
                blank=True, 
                validators=[FileExtensionValidator(allowed_extensions=['avi', 'mp4', 'wmv', 'mkv', 'ts', 'flv', 'mpeg'])])

    
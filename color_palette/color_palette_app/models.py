from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Ek profil alanları ekleyebilirsiniz

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ColorPalette(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(ImageUpload, on_delete=models.CASCADE)
    palette_image = models.ImageField(upload_to='palettes/')
    created_at = models.DateTimeField(auto_now_add=True)
from django.db import models
from django.contrib.auth.models import User

# BaseModel sınıfı
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Oluşturulma zamanı
    updated_at = models.DateTimeField(auto_now=True)  # Güncellenme zamanı

    class Meta:
        abstract = True  # Bu sınıftan doğrudan tablo oluşturulmaz

# ImageUpload modelini BaseModel'den türetme
class ImageUpload(BaseModel):
    image = models.ImageField(upload_to='uploads/')

    def __str__(self):
        return f"Image {self.id} uploaded at {self.created_at}"

# ColorPalette modelini BaseModel'den türetme
class ColorPalette(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(ImageUpload, on_delete=models.CASCADE)
    palette_image = models.ImageField(upload_to='palettes/')
    rgb_codes = models.TextField(blank=True)  # Renk kodlarını saklamak için alan

    def __str__(self):
        return f"Palette for Image {self.image.id} created by {self.user.username}"

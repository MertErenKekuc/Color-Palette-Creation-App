from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):  # basemodel sınıfı: diğer modeller için ortak alanları tanımlar
    created_at = models.DateTimeField(auto_now_add=True)  # modelin oluşturulma zamanını otomatik kaydeder
    updated_at = models.DateTimeField(auto_now=True)  # model her güncellendiğinde zaman bilgisini kaydeder

    class Meta:
        abstract = True  # bu sınıftan doğrudan tablo oluşturulmaz, diğer modeller tarafından miras alınır

# imageupload modeli: resim yüklemek için kullanılan model
class ImageUpload(BaseModel):
    image = models.ImageField(upload_to='uploads/') # yüklenen resmin depolanacağı klasör

    def __str__(self):
        return f"Image {self.id} uploaded at {self.created_at}"

# colorpalette modeli: bir kullanıcı ve resimle ilişkili renk paletini saklar
class ColorPalette(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # kullanıcıyla ilişki kurar, kullanıcı silinirse renk paleti de silinir
    image = models.ForeignKey(ImageUpload, on_delete=models.CASCADE) # imageupload ile ilişki kurar, resim silinirse palet de silinir
    palette_image = models.ImageField(upload_to='palettes/') # oluşturulan renk paletinin saklanacağı klasör
    rgb_codes = models.TextField(blank=True)  # renk kodlarını saklamak için metin alanı (json string olarak kullanılabilir)
    k_value = models.IntegerField(default=5) # k-means algoritması için küme sayısını saklar eğer hiç bir değer girilmezse default olarak 5 girilir

    def __str__(self):
        return f"Palette for Image {self.image.id} created by {self.user.username}"

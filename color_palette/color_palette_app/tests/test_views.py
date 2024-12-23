from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from color_palette_app.models import ImageUpload, ColorPalette

class ViewsTestCase(TestCase):
    """
    Görünüm (views) fonksiyonlarının birim testlerini içerir.
    - Her bir test, bir görünümün beklenen şekilde çalışıp çalışmadığını kontrol eder.
    - Kullanıcı oturumu açılarak işlemler gerçekleştirilir.
    """

    def setUp(self):
        """
        Test ortamını hazırlar:
        - Test için bir kullanıcı oluşturur.
        - Kullanıcıyı oturum açmış şekilde ayarlar.
        """
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_process_image_view(self):
        """
        /process_image/ görünümünü test eder:
        - Geçerli bir görselin POST ile yüklenmesini ve işlenmesini kontrol eder.
        - Renk paletinin oluşturulduğunu doğrular.
        """
        # Örnek bir test görseli oluştur
        with open('media/test_images/small.jpg', 'rb') as img:
            uploaded_file = SimpleUploadedFile('small.jpg', img.read(), content_type='image/jpeg')

        # POST isteği ile görseli yükleyin ve işleyin
        response = self.client.post('/process_image/', {
            'image': uploaded_file,
            'k': 5,  # KMeans için kümelerin sayısı
            'blur_kernel': 5  # Gaussian Blur için kernel boyutu
        })

        # Yanıtın başarılı olduğunu doğrula (200 OK)
        self.assertEqual(response.status_code, 200)

        # Yanıtta 'palette_image' değişkeninin bulunduğunu doğrula
        self.assertIn('palette_image', response.context)

        # Veritabanında bir ColorPalette nesnesi oluşturulduğunu doğrula
        self.assertTrue(ColorPalette.objects.exists())

    def test_edit_palette_view(self):
        """
        /edit_palette/<palette_id>/ görünümünü test eder:
        - Var olan bir renk paletinin düzenlenebilir olduğunu doğrular.
        - Güncellenen RGB kodlarını kontrol eder.
        """
        # Test için bir ImageUpload ve ColorPalette nesnesi oluştur
        image = ImageUpload.objects.create(image='test_image.jpg')
        palette = ColorPalette.objects.create(
            user=self.user,
            image=image,
            rgb_codes="#123456|#654321|#000000",
            k_value=3
        )

        # POST isteği ile paleti düzenleyin
        response = self.client.post(f'/edit_palette/{palette.id}/', {
            'rgb_codes': "#123456|#654321|#000000",  # Yeni renk kodları
            'k_value': 3  # KMeans küme sayısı (değiştirilmeden aynı)
        })

        # Yanıtın başarılı olduğunu doğrula (200 OK)
        self.assertEqual(response.status_code, 200)

        # Güncellenen paleti veritabanından tekrar al ve kontrol et
        updated_palette = ColorPalette.objects.get(id=palette.id)
        print("Güncellenen RGB Kodları:", updated_palette.rgb_codes)  # Hata ayıklama çıktısı
        self.assertIn("#123456", updated_palette.rgb_codes)  # Yeni renk kodlarının kaydedildiğini kontrol et

    def test_delete_palette_view(self):
        """
        /delete_palette/<palette_id>/ görünümünü test eder:
        - Var olan bir renk paletinin başarılı bir şekilde silindiğini doğrular.
        - Silme işleminden sonra veritabanında paletin bulunmadığını kontrol eder.
        """
        # Test için bir ImageUpload ve ColorPalette nesnesi oluştur
        image = ImageUpload.objects.create(image='test_image.jpg')
        palette = ColorPalette.objects.create(
            user=self.user,
            image=image,
            rgb_codes="#FF0000|#00FF00|#0000FF",
            k_value=3
        )

        # POST isteği ile paleti silin
        response = self.client.post(f'/delete_palette/{palette.id}/')

        # Yanıtın yönlendirme içerdiğini doğrula (302 Found)
        self.assertEqual(response.status_code, 302)

        # Veritabanında paletin artık mevcut olmadığını kontrol et
        self.assertFalse(ColorPalette.objects.filter(id=palette.id).exists())

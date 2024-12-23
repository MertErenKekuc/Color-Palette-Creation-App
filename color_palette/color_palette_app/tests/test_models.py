from django.test import TestCase
from django.contrib.auth.models import User
from color_palette_app.models import ImageUpload, ColorPalette

class ModelsTestCase(TestCase):
    def setUp(self):
        # Test kullanıcı oluştur
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_image_upload_model(self):
        # Bir görsel yükle ve modeli test et
        image = ImageUpload.objects.create(image='test_image.jpg')
        self.assertIsNotNone(image.id)
        self.assertEqual(image.image, 'test_image.jpg')

    def test_color_palette_model(self):
        # Bir ColorPalette nesnesi oluştur ve test et
        image = ImageUpload.objects.create(image='test_image.jpg')
        palette = ColorPalette.objects.create(
            user=self.user,
            image=image,
            rgb_codes="#FF0000|#00FF00|#0000FF",
            k_value=3
        )
        self.assertEqual(palette.k_value, 3)
        self.assertIn("#FF0000", palette.rgb_codes)
        self.assertEqual(palette.user, self.user)

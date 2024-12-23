from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import TestCase
from color_palette_app.views import validate_image_format

class UtilsTestCase(TestCase):
    """
    Yardımcı (utility) fonksiyonları test eden sınıf.
    """

    def test_validate_image_format_with_valid_images(self):
        """
        Geçerli görsel formatlarının kabul edildiğini kontrol eder.
        """
        # JPEG formatında bir test görseli oluştur
        valid_jpeg = SimpleUploadedFile("test_image.jpg", b"test_content", content_type="image/jpeg")
        self.assertIsNone(validate_image_format(valid_jpeg))  # ValidationError atmamalı

        # PNG formatında bir test görseli oluştur
        valid_png = SimpleUploadedFile("test_image.png", b"test_content", content_type="image/png")
        self.assertIsNone(validate_image_format(valid_png))  # ValidationError atmamalı

    def test_validate_image_format_with_invalid_images(self):
        """
        Geçersiz görsel formatlarının reddedildiğini kontrol eder.
        """
        # .txt formatında bir test dosyası oluştur
        invalid_txt = SimpleUploadedFile("test_file.txt", b"test_content", content_type="text/plain")
        with self.assertRaises(ValidationError):  # ValidationError atmalı
            validate_image_format(invalid_txt)

        # GIF formatında bir dosya oluştur
        invalid_gif = SimpleUploadedFile("test_image.gif", b"test_content", content_type="image/gif")
        with self.assertRaises(ValidationError):  # ValidationError atmalı
            validate_image_format(invalid_gif)

    def test_validate_image_format_with_corrupt_file(self):
        """
        Bozuk dosyalar için uygun hata fırlatıldığını kontrol eder.
        """
        # Bozuk veya boş bir dosya oluştur
        corrupt_file = SimpleUploadedFile("corrupt_image.jpg", b"", content_type="image/jpeg")
        with self.assertRaises(ValidationError):  # ValidationError atmalı
            validate_image_format(corrupt_file)

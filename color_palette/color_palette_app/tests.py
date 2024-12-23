import json
import time
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

class PerformanceTest(TestCase):
    def setUp(self):
        # Test kullanıcısı oluştur ve oturum aç
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_image_processing_with_different_inputs(self):
        # Örnek test görselleri
        test_images = [
            ('test_images_small.jpg', 'media/test_images/test_images_small.jpg'),
            ('test_images_medium.jpg', 'media/test_images/test_images_medium.jpg'),
            ('test_images_large.jpg', 'media/test_images/test_images_large.jpg'),
        ]

        for filename, path in test_images:
            with self.subTest(image=filename):
                with open(path, 'rb') as img_file:
                    uploaded_file = SimpleUploadedFile(filename, img_file.read(), content_type='image/jpeg')
                
                start_time = time.time()
                
                # Görsel işleme isteğini gönder
                response = self.client.post('/process_image/', {
                    'image': uploaded_file,
                    'k': 5,
                    'blur_kernel': 5
                })
                
                end_time = time.time()

                # Yanıt kontrolü
                self.assertEqual(response.status_code, 200)
                self.assertIn('palette_image', response.context)  # Palet görseli yanıt içinde olmalı
                print(f"{filename} işleme süresi: {end_time - start_time} saniye")

    def test_parametre_anlayisi(self):
        # Yeni parametre testi
        test_images = [
            ('test_images_small.jpg', 'media/test_images/test_images_small.jpg'),
        ]
        k_values = [2, 5, 10, 15, 20]
        blur_kernels = [3, 5, 7, 15, 25, 45]

        test_results = []

        for filename, path in test_images:
            for k in k_values:
                for blur_kernel in blur_kernels:
                    with self.subTest(image=filename, k=k, blur_kernel=blur_kernel):
                        with open(path, 'rb') as img_file:
                            uploaded_file = SimpleUploadedFile(filename, img_file.read(), content_type='image/jpeg')
                        
                        start_time = time.time()
                        
                        # Görsel işleme isteğini gönder
                        response = self.client.post('/process_image/', {
                            'image': uploaded_file,
                            'k': k,
                            'blur_kernel': blur_kernel
                        })
                        
                        end_time = time.time()

                        self.assertEqual(response.status_code, 200)
                        self.assertIn('palette_image', response.context)
                        
                        test_results.append({
                            'image': filename,
                            'k_value': k,
                            'blur_kernel': blur_kernel,
                            'processing_time': end_time - start_time
                        })
                        print(f"{filename} - k: {k}, blur_kernel: {blur_kernel}, İşleme süresi: {end_time - start_time}")

        with open('parametre_test_results.json', 'w') as file:
            json.dump(test_results, file)

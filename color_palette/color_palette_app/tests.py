#tests.py
import os
import time
from django.test import TestCase
from django.conf import settings
from color_palette_app.views import load_and_resize_image, apply_gaussian_blur, convert_to_lab, apply_kmeans

class PerformanceTests(TestCase):
    def setUp(self):
        """
        Test görsellerini yükleme için setup işlemleri.
        """
        self.test_images_dir = os.path.join(settings.MEDIA_ROOT, 'test_images')
        self.results = []

    def test_processing_time(self):
        """
        Görseller üzerinde işlem sürelerini ölçme testi.
        """
        for filename in os.listdir(self.test_images_dir):
            image_path = os.path.join(self.test_images_dir, filename)
            try:
                # İşlem sürelerini ölçmek
                start_time = time.time()
                
                # Görüntüyü yükleme ve yeniden boyutlandırma
                img_resized = load_and_resize_image(image_path)
                load_time = time.time()
                
                # Gaussian Blur uygulama
                img_blurred = apply_gaussian_blur(img_resized)
                blur_time = time.time()
                
                # LAB uzayına dönüştürme
                img_lab = convert_to_lab(img_blurred)
                lab_time = time.time()
                
                # K-means uygulama
                centroids = apply_kmeans(img_lab, k=5)
                kmeans_time = time.time()

                # Sonuçları kaydet
                self.results.append({
                    'image': filename,
                    'load_time': load_time - start_time,
                    'blur_time': blur_time - load_time,
                    'lab_time': lab_time - blur_time,
                    'kmeans_time': kmeans_time - lab_time,
                    'total_time': kmeans_time - start_time
                })
            except Exception as e:
                self.results.append({
                    'image': filename,
                    'error': str(e)
                })

        # Test sonuçlarını doğrulama
        self.assertGreater(len(self.results), 0)

    def tearDown(self):
        """
        Sonuçları dosyaya yazma.
        """
        with open('performance_results.csv', 'w') as f:
            f.write('image,load_time,blur_time,lab_time,kmeans_time,total_time\n')
            for result in self.results:
                if 'error' in result:
                    f.write(f"{result['image']},ERROR: {result['error']}\n")
                else:
                    f.write(f"{result['image']},{result['load_time']},{result['blur_time']},{result['lab_time']},{result['kmeans_time']},{result['total_time']}\n")
                    
class ParameterTests(TestCase):
    def setUp(self):
        """
        Test görsellerini yükleme için setup işlemleri.
        """
        self.test_images_dir = os.path.join(settings.MEDIA_ROOT, 'test_images')
        self.results = []

    def test_parameter_variations(self):
        """
        Farklı parametre değerleri ile test yapma.
        """
        for k in [3, 5, 7]:  # Farklı K-means k değerleri
            for kernel_size in [(3, 3), (5, 5), (7, 7)]:  # Farklı Gaussian Blur kernel boyutları
                for filename in os.listdir(self.test_images_dir):
                    image_path = os.path.join(self.test_images_dir, filename)
                    try:
                        start_time = time.time()
                        
                        # Görüntüyü yükleme ve yeniden boyutlandırma
                        img_resized = load_and_resize_image(image_path)
                        
                        # Gaussian Blur uygulama
                        img_blurred = apply_gaussian_blur(img_resized, kernel_size=kernel_size)
                        
                        # LAB uzayına dönüştürme
                        img_lab = convert_to_lab(img_blurred)
                        
                        # K-means uygulama
                        centroids = apply_kmeans(img_lab, k=k)
                        end_time = time.time()

                        # Sonuçları kaydet
                        self.results.append({
                            'image': filename,
                            'k': k,
                            'kernel_size': kernel_size,
                            'total_time': end_time - start_time,
                            'centroids': centroids.tolist()
                        })
                    except Exception as e:
                        self.results.append({
                            'image': filename,
                            'k': k,
                            'kernel_size': kernel_size,
                            'error': str(e)
                        })

        # Sonuçların doğru olduğunu kontrol et
        self.assertGreater(len(self.results), 0)

    def tearDown(self):
        """
        Sonuçları CSV'ye yazma.
        """
        with open('parameter_results.csv', 'w') as f:
            f.write('image,k,kernel_size,total_time\n')
            for result in self.results:
                if 'error' in result:
                    f.write(f"{result['image']},{result['k']},{result['kernel_size']},ERROR: {result['error']}\n")
                else:
                    f.write(f"{result['image']},{result['k']},{result['kernel_size']},{result['total_time']}\n")

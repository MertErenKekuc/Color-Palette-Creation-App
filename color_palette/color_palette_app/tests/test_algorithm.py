from django.test import TestCase
import numpy as np
from color_palette_app.views import apply_kmeans, convert_to_lab, lab_to_rgb

class AlgorithmTestCase(TestCase):
    """
    Görüntü işleme algoritmalarını test eden sınıf.
    """

    def test_apply_kmeans(self):
        """
        KMeans algoritmasının doğru sayıda küme oluşturduğunu kontrol eder.
        """
        fake_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        k = 5
        centroids = apply_kmeans(fake_image, k=k)
        self.assertEqual(len(centroids), k)
        for centroid in centroids:
            self.assertTrue(np.all(centroid >= 0) and np.all(centroid <= 255))

    def test_convert_to_lab(self):
        """
        Görüntünün RGB'den LAB'e doğru dönüştürüldüğünü kontrol eder.
        """
        fake_image = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
        lab_image = convert_to_lab(fake_image)
        self.assertEqual(fake_image.shape, lab_image.shape)

    def test_lab_to_rgb(self):
        """
        LAB renk uzayından RGB'ye doğru dönüşüm yapıldığını kontrol eder.
        """
        fake_lab = np.array([[50, 0, 0], [100, 0, 0], [150, 0, 0], [200, 0, 0], [255, 0, 0]], dtype=np.uint8)
        rgb_image = lab_to_rgb(fake_lab)
        self.assertEqual(rgb_image.shape, fake_lab.shape)

# Görüntüden Renk Paleti Çıkarma Uygulaması
# Bu proje Kocaeli Üniversitesi Yazılım Mühendisliği Öğrencileri tarafından Python Programlama Dersi için yapılmıştır.
# Projeyi yapan kişiler: 230229080_Ahmet_Çağlar 210229056_Dilara_Çatalçam 210229005_Mert_Eren_Keküç

Bu proje, kullanıcının yüklediği görüntülerden (JPEG ve PNG formatında) baskın renkleri belirlemek, bu renkleri görselleştirerek web arayüzünde sunmak ve renk paletlerini RGB ve hexadecimal formatında kullanıcıya sunmayı amaçlamaktadır.

## Özellikler
- Kullanıcı dostu web arayüzü ile renk paletlerinin oluşturulması ve görüntülenmesi.
- Gaussian bulanıklaştırma ve LAB renk uzayı dönüşümü gibi görüntü işleme tekniklerinin kullanımı.
- KMeans algoritmasıyla baskın renklerin kümelenmesi.
- Renk paletlerinin yönetimi ve kullanıcıya özel saklama imkanı.

## Kullanılan Teknolojiler
- **Python**: Projenin ana programlama dili.
- **Django**: Web geliştirme ve backend işlemleri için.
- **OpenCV**: Görüntü işleme (yükleme, boyutlandırma, bulanıklaştırma, renk uzayı dönüşümleri).
- **Scikit-Learn**: KMeans algoritmasının uygulanması.
- **HTML/CSS ve JavaScript**: Kullanıcı arayüzü tasarımı.
- **Bootstrap**: Responsive ve estetik arayüz tasarımı için.

## Kurulum
### Gereksinimler
- Python 3.8 veya üstü
- Sanal ortam (virtualenv) kullanımı önerilir.
- Gerekli bağımlılıklar `requirements.txt` dosyasından yüklenmelidir.

### Adımlar
1. **Proje Deposu**: Projeyi klonlayın:
   ```bash
   git clone https://github.com/MertErenKekuc/Color-Palette-Creation-App.git
   cd Color-Palette-Creation-App
   ```

2. **Sanal Ortam Kurulumu**:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # Windows için myenv\Scripts\activate
   ```

3. **Bağımlılıkları Yükleme**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Veritabanı Migrasyonu**:
   ```bash
   python manage.py migrate
   ```

5. **Sunucuyu Başlatma**:
   ```bash
   python manage.py runserver
   ```

6. **Uygulamaya Erişim**: Tarayıcıda `http://127.0.0.1:8000/` adresine gidin.

## Kullanıcı Rehberi
### Görsel Yükleme
1. Sisteme kayıt olun ve giriş yapın.
2. Ana sayfada "Dosya Seç" butonuyla görselinizi yükleyin (JPEG veya PNG formatında).
3. Renk kümeleme için `K` değeri (1-10 arası) ve bulanıklaştırma için `Kernel` değerini girin.
4. "Gönder" butonuna basarak işlemi başlatın.

### Sonuç Görüntüleme
- **Renk Paleti**: Baskın renklerin görselleştirilmiş hali.
- **Hexadecimal Kodlar**: Her rengin HEX formatı.
- **İşlenmiş Görseller**: Ara işlemler sonucu görseller.

### Palet Yönetimi
- Profil sekmesinden oluşturulan paletlere ulaşabilirsiniz.
- Paletlerinizi düzenleyebilir veya silebilirsiniz.

## Teknik Detaylar
1. **Görsel İşleme**:
   - Görseller `MEDIA_ROOT` dizininde saklanır.
   - OpenCV ile boyutlandırma, bulanıklaştırma ve renk uzayı dönüşümü gerçekleştirilir.
   - KMeans algoritması ile renk kümelenmesi yapılır.

2. **Veritabanı Yönetimi**:
   - Django ORM kullanılarak `ImageUpload` ve `ColorPalette` modelleri ile veri yönetimi.

3. **Kullanıcı Yönetimi**:
   - Django’nun dahili kullanıcı sistemi ile giriş/çıkış ve yetkilendirme.

4. **Renk Paleti Oluşturma**:
   - Görseller LAB renk uzayına dönüştürülür.
   - KMeans ile baskın renkler hesaplanır ve RGB formatına çevrilir.

## Kaynakça
- [OpenCV Documentation](https://docs.opencv.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Scikit-Learn Documentation](https://scikit-learn.org/)
- [Sentdex YouTube Kanalı](https://www.youtube.com/user/sentdex)

---

Proje hakkında detaylı bilgi için [GitHub sayfamıza](https://github.com/MertErenKekuc/Color-Palette-Creation-App) göz atabilirsiniz.

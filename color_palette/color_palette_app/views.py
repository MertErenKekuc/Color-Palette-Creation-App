import os
import cv2 # opencv'nin kütüphanesi
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ImageUploadForm, UserRegisterForm, UserUpdateForm
from .models import ImageUpload, ColorPalette
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from io import BytesIO
import base64
from sklearn.cluster import KMeans # KMeans algoritması için kullanılan kütüphane
from django.core.exceptions import ValidationError
from PIL import Image
from django.core.files.base import ContentFile

# Ortak kullanılan fonksiyonlar
def validate_image_format(uploaded_file): # görsellerin formatını doğrulayan fonksiyon 
    """
    Yüklenen görselin formatını kontrol eder. 
    Sadece JPEG ve PNG formatlarını kabul eder.
    """
    try:
        image = Image.open(uploaded_file)
        if image.format not in ['JPEG', 'PNG']:
            raise ValidationError('Sadece JPEG ve PNG formatındaki görseller desteklenir.')
    except Exception:
        raise ValidationError('Geçersiz görsel formatı.')

def load_and_resize_image(image_path, size=(200, 200)):  # görsel yükleme ve yeniden boyutlandırma fonks.
    img = cv2.imread(image_path) # görsel okuma fonksiyonu ve yolu
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}") 
    return cv2.resize(img, size)

def apply_gaussian_blur(image, kernel_size=(5, 5)): # gaussian blur fonks. kernel 5,5 parametresi alınmış test için değiştirilebilir
    return cv2.GaussianBlur(image, kernel_size, 0)

def convert_to_lab(image): # görseli RGB'den LAB renk uzayına çevirme
    return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

def apply_kmeans(image, k=5):
    """
    Görüntüdeki baskın renkleri bulmak için KMeans algoritmasını uygular.
    
    Parametreler:
    - image: İşlenecek görüntü (numpy array formatında, LAB renk uzayında olmalı).
    - k: KMeans algoritmasında kullanılacak küme sayısı (varsayılan 5).

    Dönüş:
    - kmeans.cluster_centers_: Bulunan renk kümelerinin merkez koordinatları (LAB formatında).
    """
    pixels = image.reshape((-1, 3))  # Görüntüyü 2 boyutlu bir matris haline getir (piksel sayısı x 3 renk kanalı)
    """KMeans algoritmasını başlat:
        - n_clusters: k değeri, yani kaç renk kümesi oluşturulacak
        - random_state: Tekrar edilebilirlik için sabit rastgelelik
        - max_iter: Maksimum yineleme sayısı
        - n_init: Algoritma farklı başlangıç noktalarıyla kaç kez çalıştırılacak
    """
    kmeans = KMeans(n_clusters=k, random_state=42, max_iter=1000, n_init=10) 
    kmeans.fit(pixels) # algoritmayı pikseller üzerinde çalıştırır. 
    return kmeans.cluster_centers_  # küme merkezlerini (baskın renkler) döndürür.

def lab_to_rgb(centroids): # L(ight)AB (renk bileşenler) formatındaki renkleri RGB formatına dönüştürür. centroids: LAB formatında renk merkezleri her bir kümenin merkezini hesaplar renk değerlerinin ortalamasını temsil eder.
    lab_image = np.uint8([centroids]) # LAB formatındaki renk merkezlerini uint8 türüne dönüştür (0-255 aralığında)
    rgb_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2RGB)
    return rgb_image[0]

def visualize_palette(colors): # paleti görselleştirmek için fonksiyon
    palette_width = 100 * len(colors) # paletin genişliği: Her renk için 100 piksel genişlik
    palette_height = 100
    palette_image = np.zeros((palette_height, palette_width, 3), dtype=np.uint8) # siyah bir arka plan oluştur (palet boyutlarında boş bir görsel)
    """ 
    Aşağıdaki for döngüsü her rengi görsele ekler, rengin başladığı ve bittiği yatay pixelleri alır renk değerlerini sınırlar
    palet görseline göre yerleştirir
    """
    for idx, color in enumerate(colors):
        start_x = idx * 100
        end_x = start_x + 100
        color = np.clip(color, 0, 255)
        palette_image[:, start_x:end_x, :] = color

    return palette_image

def save_palette_to_base64(palette_image):
    # Görseli base64 formatında kaydetme
    _, buffer = cv2.imencode('.png', palette_image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return img_str

def save_image_to_file(image, filename):
    # Görseli kaydetme fonksiyonu
    output_path = os.path.join('media', filename)
    cv2.imwrite(output_path, image)
    return output_path

def handle_error(request, error_message): # hataları döndürmek için kullanılan fonksiyon
    return render(request, 'error.html', {'error': error_message})

@login_required 
def home(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('process_image')
    else:
        form = ImageUploadForm()

    palettes = ColorPalette.objects.filter(user=request.user).select_related('image')
    for palette in palettes:
        palette.rgb_colors = palette.rgb_codes.split('|') if hasattr(palette, 'rgb_codes') else []

    return render(request, 'home.html', {'form': form, 'palettes': palettes})

@login_required
def process_image(request):  # görüntünün adım adım işlendiği fonksiyon
    if request.method == 'POST':
        try:
            uploaded_image = request.FILES.get('image')
            if not uploaded_image:
                return handle_error(request, 'Görsel yüklenmedi, lütfen bir görsel seçin.')
            
            # Görsel formatını doğrula
            try:
                validate_image_format(uploaded_image)
            except ValidationError as e:
                return handle_error(request, str(e))

            # Kullanıcıdan alınan k değeri
            k = request.POST.get('k', 5)
            try:
                k = int(k)
            except ValueError:
                return handle_error(request, 'Geçersiz "k" değeri. Lütfen geçerli bir sayı girin.')

            # kullanıcıdan alınan blur_kernel değeri
            blur_kernel = request.POST.get('blur_kernel', 5)
            try:
                blur_kernel = int(blur_kernel)
                if blur_kernel % 2 == 0:  # gaussian blur için kernel tek sayı olmalı
                    return handle_error(request, 'Blur kernel değeri tek sayı olmalıdır.')
            except ValueError:
                return handle_error(request, 'Geçersiz blur kernel değeri. Lütfen geçerli bir sayı girin.')

            # Görüntü işleme
            image_instance = ImageUpload.objects.create(image=uploaded_image)
            image_path = image_instance.image.path

            img_resized = load_and_resize_image(image_path) # yeniden boyutlandırma
            img_blurred = apply_gaussian_blur(img_resized, (blur_kernel, blur_kernel))  # Kullanıcıdan alınan blur değeri
            img_lab = convert_to_lab(img_blurred) # görüntü LAB formatına çevirme
            centroids_lab = apply_kmeans(img_lab, k) # LAB'a çevirilen görüntüye KMeans algoritması uygulama
            centroids_rgb = lab_to_rgb(centroids_lab) # LAB türünde olan görüntüyü RGB formatına çevirme.

            # Paleti görsel olarak oluştur
            palette_image = visualize_palette(centroids_rgb)

            # Görseli base64 formatında kaydetme
            palette_base64 = save_palette_to_base64(palette_image)
            
            # Gaussian Blur ve LAB uzayı görsellerini kaydet
            blurred_image_path = save_image_to_file(img_blurred, 'blurred_image.png')
            lab_image_path = save_image_to_file(img_lab, 'lab_image.png')

            # Renk kodlarını oluştur
            rgb_codes = ['#{:02x}{:02x}{:02x}'.format(int(c[0]), int(c[1]), int(c[2])) for c in centroids_rgb]
            rgb_code_string = '|'.join(rgb_codes)

            """ 
            Veritabanına kaydetme işlemleri
            kullanıcı,
            görsel,
            paletin görseli,
            rgb kodunu string şeklinde
            k değerini
            """
            ColorPalette.objects.create(
                user=request.user, 
                image=image_instance,
                palette_image=palette_base64,
                rgb_codes=rgb_code_string,
                k_value=k
            )

            return render(request, 'palette.html', {
                'palette_image': palette_base64,
                'rgb_codes': rgb_codes,
                'uploaded_image_url': image_instance.image.url,
                'blurred_image_url': blurred_image_path,
                'lab_image_url': lab_image_path,
                'k_value': k,
                'blur_kernel': blur_kernel
            })

        except FileNotFoundError:
            return handle_error(request, 'Görsel bulunamadı. Lütfen tekrar deneyin.')
        except Exception as e:
            return handle_error(request, f'Bilinmeyen bir hata oluştu: {str(e)}')
    else:
        return redirect('home')


@login_required
def edit_palette(request, palette_id):
    try:
        palette = get_object_or_404(ColorPalette, id=palette_id, user=request.user)
        image_instance = palette.image
        image_path = image_instance.image.path
        k = palette.k_value # daha önce belirlenen renk kümesi sayısı

        img_resized = load_and_resize_image(image_path)
        # blur kernel varsayımı veya kullanıcıdan alınması
        blur_kernel = 5  # varsayılan kernel değeri, gerekirse değiştirilir.
        img_blurred = apply_gaussian_blur(img_resized, (blur_kernel, blur_kernel))
        img_lab = convert_to_lab(img_resized)
        centroids_lab = apply_kmeans(img_lab, k)
        centroids_rgb = lab_to_rgb(centroids_lab)
        blurred_image_path = save_image_to_file(img_blurred, 'blurred_image_edit.png') # Blurlanmış görselleri oluştur ve kaydet.
        lab_image_path = save_image_to_file(img_lab, 'lab_image_edit.png') # Lab görselleri kaydetme.
        # Paleti görsel olarak oluştur
        palette_image = visualize_palette(centroids_rgb)
        # Görseli base64 formatında kaydetme
        palette_base64 = save_palette_to_base64(palette_image)
        # Renk kodlarını oluştur
        rgb_codes = ['#{:02x}{:02x}{:02x}'.format(int(c[0]), int(c[1]), int(c[2])) for c in centroids_rgb]

        # Veritabanını güncelle
        palette.palette_image = palette_base64 # yeni renk paletini kaydeder
        palette.rgb_codes = '|'.join(rgb_codes) # renk kodlarını string olarak kaydeder
        palette.save()

        """
        Test için kullanılan yönlendirme
        return redirect('home')  # Burada 'home', yönlendirme yapılacak URL'nin adı.
        """
        return render(request, 'palette.html', {
            'palette_image': palette_base64,
            'rgb_codes': rgb_codes,
            'blurred_image_url': blurred_image_path,
            'lab_image_url': lab_image_path,
            'uploaded_image_url': image_instance.image.url,
            'k_value': k
        })
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

@login_required
def delete_palette(request, palette_id):
    try:
        palette = get_object_or_404(ColorPalette, id=palette_id, user=request.user)
        palette.delete()
        return redirect('home')
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'),
                                password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})

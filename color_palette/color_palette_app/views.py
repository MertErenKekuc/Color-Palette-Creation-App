import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ImageUploadForm, UserRegisterForm
from .models import ImageUpload, ColorPalette
from django.core.files.storage import FileSystemStorage
from io import BytesIO
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout

# Ortak fonksiyonlar
def load_and_resize_image(image_path, size=(200, 200)):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    return cv2.resize(img, size)

def apply_gaussian_blur(image, kernel_size=(5, 5)):
    return cv2.GaussianBlur(image, kernel_size, 0)

def convert_to_lab(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

def apply_kmeans(image, k=5):
    # LAB renk uzayında K-means uygulaması
    pixels = image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=k, random_state=42, max_iter=500)
    kmeans.fit(pixels)
    return kmeans.cluster_centers_


def lab_to_rgb(centroids):
    # LAB renk uzayını RGB'ye doğru bir şekilde dönüştürme
    lab_image = np.uint8([centroids])
    rgb_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2RGB)
    return rgb_image[0]

def visualize_palette(colors):
    # Palet görselleştirme
    palette_width = 100 * len(colors)
    palette_height = 100
    palette_image = np.zeros((palette_height, palette_width, 3), dtype=np.uint8)

    for idx, color in enumerate(colors):
        start_x = idx * 100
        end_x = start_x + 100
        color = np.clip(color, 0, 255)  # Renk değerlerini sınırla
        palette_image[:, start_x:end_x, :] = color

    return palette_image

@login_required
def home(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('process_image')
    else:
        form = ImageUploadForm()

    # Process palettes
    palettes = ColorPalette.objects.filter(user=request.user).select_related('image')
    for palette in palettes:
        # Assuming 'rgb_codes' is a pipe-separated string of hex codes in the database
        palette.rgb_colors = palette.rgb_codes.split('|') if hasattr(palette, 'rgb_codes') else []

    return render(request, 'home.html', {'form': form, 'palettes': palettes})

@login_required
def process_image(request):
    if request.method == 'POST':
        try:
            uploaded_image = request.FILES.get('image')
            if not uploaded_image:
                return render(request, 'error.html', {'error': 'No image provided.'})

            k = int(request.POST.get('k', 5))  # Kullanıcıdan alınan `k` değeri
            image_instance = ImageUpload.objects.create(image=uploaded_image)
            image_path = image_instance.image.path

            # Görüntü işleme
            img_resized = load_and_resize_image(image_path)
            img_lab = convert_to_lab(img_resized)
            centroids_lab = apply_kmeans(img_lab, k)
            centroids_rgb = lab_to_rgb(centroids_lab)

            # Paleti görsel olarak oluştur
            palette_image = visualize_palette(centroids_rgb)

            # Görseli dosyaya kaydet
            palette_path = f'media/palettes/palette_{image_instance.id}.png'
            cv2.imwrite(palette_path, cv2.cvtColor(palette_image, cv2.COLOR_RGB2BGR))

            # Renk kodlarını oluştur
            rgb_codes = ['#{:02x}{:02x}{:02x}'.format(int(c[0]), int(c[1]), int(c[2])) for c in centroids_rgb]
            rgb_code_string = '|'.join(rgb_codes)

            # Veritabanına kaydet
            ColorPalette.objects.create(
                user=request.user,
                image=image_instance,
                palette_image=f'palettes/palette_{image_instance.id}.png',
                rgb_codes=rgb_code_string,
                k_value=k  # Burada `k` değerini kaydediyoruz
            )

            return render(request, 'palette.html', {
                'palette_image': f'/media/palettes/palette_{image_instance.id}.png',
                'rgb_codes': rgb_codes,
                'uploaded_image_url': image_instance.image.url,
                'k_value': k
            })
        except Exception as e:
            return render(request, 'error.html', {'error': str(e)})
    else:
        return redirect('home')

@login_required
def edit_palette(request, palette_id):
    try:
        # Kullanıcıya ait paleti al
        palette = get_object_or_404(ColorPalette, id=palette_id, user=request.user)
        image_instance = palette.image
        image_path = image_instance.image.path

        # Kaydedilmiş `k` değerini al
        k = palette.k_value  # Veritabanından gelen `k` değeri

        # Görüntü işleme
        img_resized = load_and_resize_image(image_path)
        img_lab = convert_to_lab(img_resized)
        centroids_lab = apply_kmeans(img_lab, k)
        centroids_rgb = lab_to_rgb(centroids_lab)

        # Paleti görsel olarak oluştur
        palette_image = visualize_palette(centroids_rgb)

        # Görseli dosyaya kaydet
        palette_path = f'media/palettes/palette_{image_instance.id}_edited.png'
        cv2.imwrite(palette_path, cv2.cvtColor(palette_image, cv2.COLOR_RGB2BGR))

        # Renk kodlarını oluştur
        rgb_codes = ['#{:02x}{:02x}{:02x}'.format(int(c[0]), int(c[1]), int(c[2])) for c in centroids_rgb]

        # Veritabanını güncelle
        palette.palette_image = f'palettes/palette_{image_instance.id}_edited.png'
        palette.rgb_codes = '|'.join(rgb_codes)
        palette.save()

        return render(request, 'palette.html', {
            'palette_image': f'/media/palettes/palette_{image_instance.id}_edited.png',
            'rgb_codes': rgb_codes,
            'uploaded_image_url': image_instance.image.url,
            'k_value': k  # `k` değerini template'e gönder
        })
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

@login_required
def delete_palette(request, palette_id):
    try:
        # Kullanıcıya ait renk paletini bul
        palette = get_object_or_404(ColorPalette, id=palette_id, user=request.user)
        palette.delete()  # Paleti sil
        return redirect('home')  # Ana sayfaya yönlendir
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

def register(request):
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
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

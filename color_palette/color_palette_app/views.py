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
    pixels = image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(pixels)
    return np.uint8(kmeans.cluster_centers_)

def lab_to_rgb(centroids):
    return cv2.cvtColor(np.uint8([centroids]), cv2.COLOR_LAB2RGB)[0]

def visualize_palette(colors):
    fig, ax = plt.subplots(figsize=(8, 4))
    hex_codes = []
    for i, color in enumerate(colors):
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(color[0]), int(color[1]), int(color[2]))
        hex_codes.append(hex_color)
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=np.array(color) / 255))
    ax.axis('off')
    return fig, hex_codes

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
            # Görüntüyü al
            uploaded_image = request.FILES.get('image')
            if not uploaded_image:
                return render(request, 'error.html', {'error': 'No image provided.'})

            # Kullanıcıdan gelen k değerini al
            k = int(request.POST.get('k', 5))

            # Görüntüyü kaydet
            image_instance = ImageUpload.objects.create(image=uploaded_image)

            # İşleme başla
            image_path = image_instance.image.path
            img_resized = load_and_resize_image(image_path)
            img_blurred = apply_gaussian_blur(img_resized)
            img_lab = convert_to_lab(img_blurred)
            centroids_lab = apply_kmeans(img_lab, k)
            centroids_rgb = lab_to_rgb(centroids_lab)

            # Renk paletini görselleştirme
            fig, rgb_codes = visualize_palette(centroids_rgb)
            buffer = BytesIO()
            FigureCanvas(fig).print_png(buffer)
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            # Paleti kaydetme
            fs = FileSystemStorage()
            palette_image_path = f'palettes/palette_{image_instance.id}.png'
            filename = fs.save(palette_image_path, BytesIO(image_png))
            palette_image_url = fs.url(filename)

            # Veritabanına kaydet
            rgb_code_string = '|'.join([f"{color}" for color in rgb_codes])
            ColorPalette.objects.create(
                user=request.user,
                image=image_instance,
                palette_image=filename,
                rgb_codes=rgb_code_string
            )

            return render(request, 'palette.html', {
                'palette_image': base64.b64encode(image_png).decode('utf-8'),
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

        # Görüntü işleme adımları
        img_resized = load_and_resize_image(image_path)
        img_blurred = apply_gaussian_blur(img_resized)
        img_lab = convert_to_lab(img_blurred)
        centroids_lab = apply_kmeans(img_lab, k=5)
        centroids_rgb = lab_to_rgb(centroids_lab)

        # Renk paletini görselleştirme
        fig, rgb_codes = visualize_palette(centroids_rgb)
        buffer = BytesIO()
        FigureCanvas(fig).print_png(buffer)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Güncellenmiş paleti kaydet
        fs = FileSystemStorage()
        palette_image_path = f'palettes/palette_{image_instance.id}_edited.png'
        filename = fs.save(palette_image_path, BytesIO(image_png))
        palette.palette_image = filename
        palette.save()

        return render(request, 'palette.html', {
            'palette_image': base64.b64encode(image_png).decode('utf-8'),
            'rgb_codes': rgb_codes,
            'uploaded_image_url': image_instance.image.url
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

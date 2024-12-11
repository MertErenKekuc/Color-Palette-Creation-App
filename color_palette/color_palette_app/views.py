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
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.shortcuts import redirect

# 1. ve 2. pipeline: Görüntü yükleme ve yeniden boyutlandırma
def load_and_resize_image(image_path, size=(200, 200)):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    img_resized = cv2.resize(img, size)
    return img_resized

# 4. pipeline: RGB'den LAB uzayına dönüştürme
def convert_to_lab(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

# 3. pipeline: Gaussian Blur uygulama
def apply_gaussian_blur(image, kernel_size=(5, 5)):
    return cv2.GaussianBlur(image, kernel_size, 0)

# K-means uygulama ve renk kümelerini çıkarma
def apply_kmeans(image, k=5):
    pixels = image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(pixels)
    centroids = kmeans.cluster_centers_
    return np.uint8(centroids)

# LAB'den RGB'ye çevirme
def lab_to_rgb(centroids):
    return cv2.cvtColor(np.uint8([centroids]), cv2.COLOR_LAB2RGB)[0]

# Renk paleti görselleştirme ve Hex kodları gösterme
def visualize_palette(colors):
    fig, ax = plt.subplots(figsize=(8, 4))
    rgb_codes = []
    for i, color in enumerate(colors):
        rgb_color = color
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]))
        rgb_codes.append(f"RGB: {rgb_color.tolist()} Hex: {hex_color}")
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=rgb_color / 255))
        ax.text(i + 0.5, -0.1, f"RGB: {rgb_color}\nHex: {hex_color}", ha='center', va='top', fontsize=9)
    ax.set_xlim(0, len(colors))
    ax.set_ylim(-0.2, 1)
    ax.axis('off')
    return fig, rgb_codes

@login_required
def home(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('process_image')
    else:
        form = ImageUploadForm()
    palettes = ColorPalette.objects.filter(user=request.user)
    return render(request, 'home.html', {'form': form, 'palettes': palettes})

@login_required
def process_image(request):
    try:
        image_instance = ImageUpload.objects.latest('uploaded_at')
        image_path = image_instance.image.path

        # Dosya yolunu kontrol etme
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # 1. ve 2. pipeline: Görüntü yükleme ve yeniden boyutlandırma
        img_resized = load_and_resize_image(image_path)

        # 3. pipeline: Gaussian Blur uygulama
        img_blurred = apply_gaussian_blur(img_resized)

        # 4. pipeline: LAB uzayına dönüştürme
        img_lab = convert_to_lab(img_blurred)

        # 5. pipeline: K-means uygulama
        k = 5
        centroids_lab = apply_kmeans(img_lab, k)
        centroids_rgb = lab_to_rgb(centroids_lab)

        # 6. pipeline: Renkleri görselleştirme
        fig, rgb_codes = visualize_palette(centroids_rgb)
        canvas = FigureCanvas(fig)
        buffer = BytesIO()
        canvas.print_png(buffer)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        image_base64 = base64.b64encode(image_png).decode('utf-8')

        # Paleti kaydetme
        palette_image_path = f'palettes/palette_{image_instance.id}.png'
        fs = FileSystemStorage()
        filename = fs.save(palette_image_path, BytesIO(image_png))
        palette_image_url = fs.url(filename)

        # Paleti veritabanına kaydetme
        ColorPalette.objects.create(user=request.user, image=image_instance, palette_image=filename)

        return render(request, 'palette.html', {'palette_image': image_base64, 'rgb_codes': rgb_codes, 'uploaded_image_url': image_instance.image.url})
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

@login_required
def edit_palette(request, palette_id):
    palette = get_object_or_404(ColorPalette, id=palette_id, user=request.user)
    image_instance = palette.image
    image_path = image_instance.image.path

    try:
        # Dosya yolunu kontrol etme
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # 1. ve 2. pipeline: Görüntü yükleme ve yeniden boyutlandırma
        img_resized = load_and_resize_image(image_path)

        # 3. pipeline: Gaussian Blur uygulama
        img_blurred = apply_gaussian_blur(img_resized)

        # 4. pipeline: LAB uzayına dönüştürme
        img_lab = convert_to_lab(img_blurred)

        # 5. pipeline: K-means uygulama
        k = 5
        centroids_lab = apply_kmeans(img_lab, k)
        centroids_rgb = lab_to_rgb(centroids_lab)

        # 6. pipeline: Renkleri görselleştirme
        fig, rgb_codes = visualize_palette(centroids_rgb)
        canvas = FigureCanvas(fig)
        buffer = BytesIO()
        canvas.print_png(buffer)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        image_base64 = base64.b64encode(image_png).decode('utf-8')

        # Paleti kaydetme
        palette_image_path = f'palettes/palette_{image_instance.id}.png'
        fs = FileSystemStorage()
        filename = fs.save(palette_image_path, BytesIO(image_png))
        palette_image_url = fs.url(filename)

        # Paleti veritabanına güncelleme
        palette.palette_image = filename
        palette.save()

        return render(request, 'palette.html', {'palette_image': image_base64, 'rgb_codes': rgb_codes, 'uploaded_image_url': image_instance.image.url})
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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Logout sonrası login sayfasına yönlendirme

@login_required
def delete_palette(request, palette_id):
    palette = ColorPalette.objects.get(id=palette_id, user=request.user)
    if palette:
        palette.delete()
    return redirect('home')
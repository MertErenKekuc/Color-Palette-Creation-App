from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.register, name='register'),  # İlk olarak register açılsın
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Logout işlemi GET ve POST destekler
    path('home/', views.home, name='home'),
    path('process_image/', views.process_image, name='process_image'),
    path('delete_palette/<int:palette_id>/', views.delete_palette, name='delete_palette'),
    path('edit_palette/<int:palette_id>/', views.edit_palette, name='edit_palette'),
    path('update_profile/', views.update_profile, name='update_profile'),
]
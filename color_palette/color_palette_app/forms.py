from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ImageUpload # kendi tanımladığımız model (resim yükleme için)

class UserRegisterForm(UserCreationForm):
    """
    Kullanıcı kayıt formu: django'nun hazır UserCreationForm sınıfını genişletir.
    Kullanıcının kullanıcı adı, e-posta adresi ve şifre oluşturmasını sağlar.
    """
    class Meta:
        model = User # form için kullanılacak model
        fields = ['username', 'email', 'password1', 'password2']

class ImageUploadForm(forms.ModelForm):
    """
    Resim yükleme formu: ImageUpload modeline dayanır.
    Kullanıcıların resim dosyalarını yüklemelerine olanak tanır.
    """
    class Meta:
        model = ImageUpload
        fields = ['image']

class UserUpdateForm(forms.ModelForm):
    """
    Kullanıcı bilgileri güncelleme formu: Kullanıcı modeline dayanır.
    Kullanıcıların kullanıcı adını ve e-posta adresini güncellemelerine olanak tanır.
    """
    class Meta:
        model = User
        fields = ['username', 'email']
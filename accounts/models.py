import os
from django.contrib.auth.models import AbstractUser
from django.db import models

def user_profile_picture_path(instance, filename):
    # Le fichier sera uploadé dans MEDIA_ROOT/profile_pics/user_<id>/<filename>
    ext = filename.split('.')[-1]
    filename = f'profile_pic.{ext}'
    return os.path.join('profile_pics', f'user_{instance.id}', filename)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('admin', 'Administrateur'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    address = models.TextField(blank=True, verbose_name='Adresse')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ville')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Code postal')
    country = models.CharField(max_length=100, blank=True, verbose_name='Pays')
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, blank=True, null=True, verbose_name='Photo de profil')
    
    def __str__(self):
        return self.email or self.username

"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URL d'administration
    path('admin/', admin.site.urls),
    
    # URL de l'application accounts
    path('accounts/', include('accounts.urls')),
    
    # URL du catalogue
    path('', include('catalog.urls')),
    
    # URLs des commandes
    path('commandes/', include('orders.urls', namespace='orders')),
    
    # URLs du panier
    path('panier/', include('cart.urls', namespace='cart')),
    
    # URLs d'authentification (pour les vues intégrées de Django)
    path('accounts/', include('django.contrib.auth.urls')),
]

from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Vue du panier
    path('', views.vue_panier, name='panier'),
    
    # Actions sur le panier
    path('ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('maj/<int:article_id>/', views.mettre_a_jour_panier, name='mettre_a_jour_panier'),
    path('supprimer/<int:article_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    
    # API pour le panier
    path('api/nombre-articles/', views.nombre_articles_panier, name='nombre_articles_panier'),
]

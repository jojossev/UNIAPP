from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Page d'accueil
    path('', views.AccueilView.as_view(), name='accueil'),
    
    # Liste des produits
    path('produits/', views.ListeProduitsView.as_view(), name='liste_produits'),
    
    # Produits par catégorie
    path('categorie/<slug:categorie_slug>/', views.ListeProduitsView.as_view(), name='produits_par_categorie'),
    
    # Détail d'un produit
    path('produit/<slug:slug>/', views.DetailProduitView.as_view(), name='detail_produit'),
    
    # Liste des catégories
    path('categories/', views.ListeCategoriesView.as_view(), name='liste_categories'),
    
    # Recherche
    path('recherche/', views.ResultatsRechercheView.as_view(), name='recherche'),
    
    # Nouveautés
    path('nouveautes/', views.NouveautesView.as_view(), name='nouveautes'),
    
    # Promotions
    path('promotions/', views.PromotionsView.as_view(), name='promotions'),
    
    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),
]

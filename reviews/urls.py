from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'reviews'

urlpatterns = [
    # Liste des avis d'un produit
    path(
        'product/<int:product_id>/reviews/',
        views.ProductReviewListView.as_view(),
        name='product_reviews'
    ),
    
    # Créer un nouvel avis
    path(
        'product/<int:product_id>/review/create/',
        views.ReviewCreateView.as_view(),
        name='review_create'
    ),
    
    # Modifier un avis existant
    path(
        'review/<int:review_id>/edit/',
        views.ReviewUpdateView.as_view(),
        name='review_edit'
    ),
    
    # Supprimer un avis
    path(
        'review/<int:pk>/delete/',
        views.ReviewDeleteView.as_view(),
        name='review_delete'
    ),
    
    # Aimer/Ne plus aimer un avis (AJAX)
    path(
        'review/<int:review_id>/like/',
        views.toggle_review_like,
        name='toggle_review_like'
    ),
]

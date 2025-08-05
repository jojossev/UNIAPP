from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from catalog.models import Produit as Product

class Review(models.Model):
    """
    Modèle représentant un avis utilisateur sur un produit.
    """
    RATING_CHOICES = [
        (1, '1 étoile - Très mauvais'),
        (2, '2 étoiles - Mauvais'),
        (3, '3 étoiles - Moyen'),
        (4, '4 étoiles - Bon'),
        (5, '5 étoiles - Excellent'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Utilisateur'
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Produit'
    )
    
    rating = models.PositiveSmallIntegerField(
        'Note',
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Note de 1 à 5 étoiles'
    )
    
    title = models.CharField(
        'Titre',
        max_length=200,
        help_text='Titre de votre avis'
    )
    
    comment = models.TextField(
        'Commentaire',
        max_length=2000,
        help_text='Votre avis détaillé sur le produit'
    )
    
    created_at = models.DateTimeField('Date de création', auto_now_add=True)
    updated_at = models.DateTimeField('Dernière mise à jour', auto_now=True)
    
    # Pour vérifier si l'utilisateur a acheté le produit avant de laisser un avis
    is_purchased = models.BooleanField(
        'Acheté',
        default=False,
        help_text='Si l\'utilisateur a acheté ce produit'
    )
    
    # Pour gérer la modération des avis
    is_approved = models.BooleanField(
        'Approuvé',
        default=True,
        help_text='Si l\'avis est approuvé par un modérateur'
    )
    
    # Pour les mentions "J'aime" sur les avis
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_reviews',
        blank=True,
        verbose_name='Utilisateurs qui ont aimé cet avis'
    )
    
    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_review',
                violation_error_message='Vous avez déjà laissé un avis pour ce produit.'
            )
        ]
    
    def __str__(self):
        return f'Avis de {self.user.username} sur {self.product.name} ({self.rating}/5)'
    
    def get_rating_display_class(self):
        """
        Retourne une classe CSS en fonction de la note.
        Utile pour le style des étoiles dans les templates.
        """
        return {
            1: 'text-danger',
            2: 'text-warning',
            3: 'text-info',
            4: 'text-primary',
            5: 'text-success',
        }.get(self.rating, '')
    
    def can_edit(self, user):
        """
        Vérifie si l'utilisateur peut modifier cet avis.
        """
        return user.is_authenticated and (user == self.user or user.is_staff)
    
    def can_delete(self, user):
        """
        Vérifie si l'utilisateur peut supprimer cet avis.
        """
        return self.can_edit(user)

from django.db import models
from catalog.models import Produit
from django.conf import settings

class Panier(models.Model):
    """Modèle représentant un panier d'achat."""
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='panier',
        verbose_name="Utilisateur"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
        ordering = ['-date_mise_a_jour']

    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

    @property
    def total(self):
        """Calcule le total du panier."""
        return sum(item.sous_total for item in self.items.all())

    @property
    def nombre_articles(self):
        """Retourne le nombre total d'articles dans le panier."""
        return sum(item.quantite for item in self.items.all())


class ArticlePanier(models.Model):
    """Modèle représentant un article dans le panier."""
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Panier"
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='panier_items',
        verbose_name="Produit"
    )
    quantite = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix unitaire"
    )
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        ordering = ['-date_ajout']
        unique_together = ['panier', 'produit']

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    @property
    def sous_total(self):
        """Calcule le sous-total pour cet article."""
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        """Sauvegarde l'article avec le prix actuel du produit."""
        # Utilise le prix promotionnel s'il existe, sinon le prix normal
        if hasattr(self.produit, 'prix_promotionnel') and self.produit.prix_promotionnel:
            self.prix_unitaire = self.produit.prix_promotionnel
        else:
            self.prix_unitaire = self.produit.prix
        super().save(*args, **kwargs)

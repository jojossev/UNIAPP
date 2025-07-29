from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class Commande(models.Model):
    """
    Modèle représentant une commande passée par un utilisateur.
    """
    # Choix pour le statut de la commande
    STATUT_EN_COURS = 'en_cours'
    STATUT_LIVRE = 'livre'
    STATUT_ANNULE = 'annule'
    
    CHOIX_STATUT = [
        (STATUT_EN_COURS, 'En cours de traitement'),
        (STATUT_LIVRE, 'Livré'),
        (STATUT_ANNULE, 'Annulé'),
    ]
    
    # Informations de base
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commandes',
        verbose_name="Utilisateur"
    )
    date_commande = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de la commande"
    )
    date_mise_a_jour = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )
    statut = models.CharField(
        max_length=20,
        choices=CHOIX_STATUT,
        default=STATUT_EN_COURS,
        verbose_name="Statut de la commande"
    )
    
    # Informations de livraison
    adresse_livraison = models.TextField(
        verbose_name="Adresse de livraison"
    )
    code_postal = models.CharField(
        max_length=10,
        verbose_name="Code postal"
    )
    ville = models.CharField(
        max_length=100,
        verbose_name="Ville"
    )
    pays = models.CharField(
        max_length=100,
        verbose_name="Pays"
    )
    
    # Informations de paiement
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant total"
    )
    paye = models.BooleanField(
        default=False,
        verbose_name="Commande payée"
    )
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']
    
    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur.email} - {self.get_statut_display()}"
    
    def est_annulable(self):
        """Vérifie si la commande peut être annulée."""
        return self.statut == self.STATUT_EN_COURS
    
    def marquer_comme_livre(self):
        """Marque la commande comme livrée."""
        if self.statut == self.STATUT_EN_COURS:
            self.statut = self.STATUT_LIVRE
            self.save()
            return True
        return False
    
    def annuler(self):
        """Annule la commande si possible."""
        if self.est_annulable():
            self.statut = self.STATUT_ANNULE
            self.save()
            return True
        return False


class LigneCommande(models.Model):
    """
    Modèle représentant une ligne de commande (un article dans une commande).
    """
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name="Commande"
    )
    produit = models.ForeignKey(
        'catalog.Produit',
        on_delete=models.PROTECT,
        related_name='lignes_commande',
        verbose_name="Produit"
    )
    quantite = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantité"
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire"
    )
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
    
    def __str__(self):
        return f"{self.quantite}x {self.produit.nom} - {self.prix_total()} €"
    
    def prix_total(self):
        """Calcule le prix total de la ligne de commande."""
        return self.quantite * self.prix_unitaire

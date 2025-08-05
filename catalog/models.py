from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import os


def product_image_path(instance, filename):
    # Génère un chemin pour l'image du produit : catalog/products/ID_PRODUIT/filename
    return f'catalog/products/{instance.produit.id}/{filename}'


def categorie_image_path(instance, filename):
    # Génère un chemin pour l'image de la catégorie : catalog/categories/ID_CATEGORIE/filename
    return f'catalog/categories/{instance.categorie.id}/{filename}'


class Categorie(models.Model):
    """Modèle représentant une catégorie de produits."""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=150, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='catalog/categories/', blank=True, null=True, verbose_name="Image de la catégorie")
    est_active = models.BooleanField(default=True, verbose_name="Active")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom
        
    @property
    def average_rating(self):
        """Calcule la note moyenne des avis approuvés pour ce produit."""
        from django.db.models import Avg
        return self.avis.filter(approuve=True).aggregate(avg_rating=Avg('note'))['avg_rating']
    
    def get_rating_stats(self):
        """Retourne un dictionnaire avec le nombre d'avis par note."""
        from django.db.models import Count
        stats = {i: 0 for i in range(1, 6)}
        queryset = self.avis.filter(approuve=True).values('note').annotate(count=Count('id'))
        
        for item in queryset:
            stats[item['note']] = item['count']
            
        return stats
    
    def get_rating_percentages(self):
        """Retourne un dictionnaire avec le pourcentage d'avis pour chaque note."""
        stats = self.get_rating_stats()
        total = sum(stats.values())
        
        if total == 0:
            return {i: 0 for i in range(1, 6)}
            
        return {i: (count / total) * 100 for i, count in stats.items()}

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:categorie_detail', kwargs={'slug': self.slug})


class ImageCategorie(models.Model):
    """Modèle pour stocker plusieurs images par catégorie."""
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Catégorie associée"
    )
    image = models.ImageField(upload_to=categorie_image_path, verbose_name="Image")
    legende = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    est_principale = models.BooleanField(default=False, verbose_name="Image principale")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Image de catégorie"
        verbose_name_plural = "Images des catégories"
        ordering = ['ordre', 'date_ajout']

    def __str__(self):
        return f"Image pour {self.categorie.nom}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule image est marquée comme principale
        if self.est_principale:
            ImageCategorie.objects.filter(categorie=self.categorie, est_principale=True).update(est_principale=False)
        super().save(*args, **kwargs)


class Produit(models.Model):
    """Modèle représentant un produit dans le catalogue."""
    # Informations de base
    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")
    nom = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Description complète")
    resume = models.CharField(max_length=255, blank=True, verbose_name="Résumé")
    
    # Prix et disponibilité
    prix = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire"
    )
    prix_promotionnel = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix promotionnel"
    )
    en_stock = models.BooleanField(default=True, verbose_name="En stock")
    quantite = models.PositiveIntegerField(default=0, verbose_name="Quantité disponible")
    
    # Catégorisation
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='produits',
        verbose_name="Catégorie"
    )
    
    # Métadonnées
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    est_nouveau = models.BooleanField(default=False, verbose_name="Nouveau produit")
    est_meilleur_vente = models.BooleanField(default=False, verbose_name="Meilleure vente")
    
    # Gestion des dates
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    date_publication = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Date de publication"
    )
    
    # SEO
    meta_titre = models.CharField(max_length=70, blank=True, verbose_name="Méta-titre (SEO)")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Méta-description (SEO)")
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['nom']),
            models.Index(fields=['-date_creation']),
        ]

    def __str__(self):
        return f"{self.nom} ({self.reference})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.nom}-{self.reference}")
        
        if not self.meta_titre:
            self.meta_titre = f"{self.nom} | {settings.SITE_NAME}"
            
        if not self.meta_description and self.resume:
            self.meta_description = self.resume[:160]
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:detail_produit', kwargs={'slug': self.slug})
        
    def has_purchased_by_user(self, user):
        """
        Vérifie si l'utilisateur a déjà acheté ce produit.
        Retourne True si l'utilisateur a commandé ce produit au moins une fois.
        """
        if not user.is_authenticated:
            return False
            
        from orders.models import OrderItem
        return OrderItem.objects.filter(
            order__user=user,
            order__status__in=['completed', 'delivered'],  # Seules les commandes terminées ou livrées
            product=self,
            quantity__gt=0
        ).exists()
    
    def est_en_promotion(self):
        """Vérifie si le produit est en promotion."""
        return self.prix_promotionnel is not None and self.prix_promotionnel < self.prix
    
    def get_prix_affichage(self):
        """Retourne le prix à afficher (prix promotionnel si disponible)."""
        return self.prix_promotionnel if self.est_en_promotion() else self.prix
    
    def get_pourcentage_promotion(self):
        """Calcule le pourcentage de réduction si le produit est en promotion."""
        if self.est_en_promotion():
            reduction = ((self.prix - self.prix_promotionnel) / self.prix) * 100
            return int(round(reduction))
        return 0
        
    def get_economie(self):
        """Calcule l'économie réalisée lorsque le produit est en promotion."""
        if self.est_en_promotion():
            return self.prix - self.prix_promotionnel
        return 0
        
    def get_courte_description(self):
        """Retourne la description courte (résumé) ou les premiers mots de la description complète si le résumé n'est pas disponible."""
        if self.resume:
            return self.resume
        # Retourne les 30 premiers mots de la description complète si le résumé n'est pas disponible
        return ' '.join(self.description.split()[:30]) + '...'
        
    @property
    def average_rating(self):
        """
        Retourne la note moyenne du produit sur 5.
        """
        from django.db.models import Avg
        result = self.avis.filter(approuve=True).aggregate(avg_rating=Avg('note'))
        return result['avg_rating'] or 0
        
    @property
    def rating_count(self):
        """
        Retourne le nombre total d'avis approuvés pour ce produit.
        """
        return self.avis.filter(approuve=True).count()
        
    def get_rating_stats(self):
        """
        Retourne un dictionnaire avec le nombre d'avis par note (1 à 5).
        
        Returns:
            dict: Un dictionnaire avec comme clés les notes (1-5) et comme valeurs
                  le nombre d'avis pour chaque note.
                  Exemple: {1: 2, 2: 0, 3: 5, 4: 3, 5: 10}
        """
        from django.db.models import Count
        
        # Initialiser un dictionnaire avec des compteurs à zéro pour chaque note
        stats = {i: 0 for i in range(1, 6)}
        
        # Récupérer le nombre d'avis groupés par note
        ratings = self.avis.filter(approuve=True).values('note').annotate(count=Count('id'))
        
        # Mettre à jour le dictionnaire avec les valeurs réelles
        for item in ratings:
            stats[item['note']] = item['count']
            
        return stats
        
    def get_rating_percentages(self):
        """
        Retourne un dictionnaire avec le pourcentage d'avis pour chaque note (1 à 5).
        
        Returns:
            dict: Un dictionnaire avec comme clés les notes (1-5) et comme valeurs
                  le pourcentage d'avis pour chaque note.
                  Exemple: {1: 10, 2: 0, 3: 25, 4: 15, 5: 50}
        """
        total_reviews = self.rating_count
        if total_reviews == 0:
            return {i: 0 for i in range(1, 6)}
            
        stats = self.get_rating_stats()
        return {rating: int((count / total_reviews) * 100) for rating, count in stats.items()}
        
    def has_purchased_by_user(self, user):
        """
        Vérifie si un utilisateur a déjà acheté ce produit.
        
        Args:
            user: L'instance de l'utilisateur à vérifier
            
        Returns:
            bool: True si l'utilisateur a déjà acheté ce produit, False sinon
        """
        if not user.is_authenticated:
            return False
            
        # Vérifier si l'utilisateur a une commande avec ce produit
        from orders.models import Commande, LigneCommande
        
        return LigneCommande.objects.filter(
            commande__utilisateur=user,
            commande__statut__in=[Commande.PAYEE, Commande.EXPEDIEE, Commande.LIVREE],
            produit=self
        ).exists()


class ImageProduit(models.Model):
    """Modèle pour stocker plusieurs images par produit."""
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Produit associé"
    )
    image = models.ImageField(upload_to=product_image_path, verbose_name="Image")
    legende = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    est_principale = models.BooleanField(default=False, verbose_name="Image principale")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produits"
        ordering = ['ordre', 'date_ajout']
    
    def __str__(self):
        return f"Image de {self.produit.nom}"
    
    def save(self, *args, **kwargs):
        # Si c'est la première image du produit, la définir comme principale
        if not self.produit.images.exists():
            self.est_principale = True
        super().save(*args, **kwargs)
        
        # S'assurer qu'une seule image est marquée comme principale
        if self.est_principale:
            ImageProduit.objects.filter(produit=self.produit).exclude(pk=self.pk).update(est_principale=False)


class AvisProduit(models.Model):
    """Modèle pour les avis des clients sur les produits."""
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name='avis',
        verbose_name="Produit"
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='avis_produits',
        verbose_name="Utilisateur"
    )
    note = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note (sur 5)"
    )
    titre = models.CharField(max_length=200, verbose_name="Titre de l'avis")
    commentaire = models.TextField(verbose_name="Commentaire")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    approuve = models.BooleanField(default=False, verbose_name="Approuvé")
    
    class Meta:
        verbose_name = "Avis produit"
        verbose_name_plural = "Avis produits"
        ordering = ['-date_creation']
        unique_together = ['produit', 'utilisateur']
    
    def __str__(self):
        return f"Avis de {self.utilisateur} sur {self.produit.nom}"


class CaracteristiqueProduit(models.Model):
    """Modèle pour les caractéristiques techniques des produits."""
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name='caracteristiques',
        verbose_name="Produit"
    )
    nom = models.CharField(max_length=100, verbose_name="Nom de la caractéristique")
    valeur = models.CharField(max_length=255, verbose_name="Valeur")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    class Meta:
        verbose_name = "Caractéristique produit"
        verbose_name_plural = "Caractéristiques produits"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return f"{self.nom}: {self.valeur}"

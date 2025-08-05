from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Categorie, Produit, ImageProduit, AvisProduit, CaracteristiqueProduit, ImageCategorie


class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 1
    fields = ('image', 'legende', 'est_principale', 'ordre', 'apercu_image')
    readonly_fields = ('apercu_image',)
    
    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "Aucune image"
    apercu_image.short_description = 'Aperçu'


class CaracteristiqueProduitInline(admin.TabularInline):
    model = CaracteristiqueProduit
    extra = 1
    fields = ('nom', 'valeur', 'ordre')


class AvisProduitInline(admin.TabularInline):
    model = AvisProduit
    extra = 0
    readonly_fields = ('utilisateur', 'note', 'titre', 'commentaire', 'date_creation')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class ImageCategorieInline(admin.TabularInline):
    model = ImageCategorie
    extra = 1
    fields = ('image', 'apercu_image', 'legende', 'est_principale', 'ordre')
    readonly_fields = ('apercu_image',)
    
    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px; object-fit: contain;" />', obj.image.url)
        return "Aucune image"
    apercu_image.short_description = 'Aperçu'


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'est_active', 'nb_produits', 'apercu_image_principale')
    list_filter = ('est_active',)
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    readonly_fields = ('date_creation', 'date_mise_a_jour', 'apercu_image', 'apercu_image_principale')
    inlines = [ImageCategorieInline]
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('nom', 'slug', 'description', 'est_active')
        }),
        (_('Image principale'), {
            'fields': ('image', 'apercu_image')
        }),
        (_('Galerie d\'images'), {
            'fields': ('apercu_image_principale',)
        }),
        (_('Métadonnées'), {
            'classes': ('collapse',),
            'fields': ('date_creation', 'date_mise_a_jour'),
        }),
    )
    
    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 100%; object-fit: contain;" />', obj.image.url)
        return "Aucune image"
    apercu_image.short_description = 'Aperçu de l\'image principale'
    
    def apercu_image_principale(self, obj):
        images = obj.images.filter(est_principale=True).first()
        if images:
            return format_html('<p>Image principale actuelle :</p><img src="{}" style="max-height: 100px; max-width: 100%; object-fit: contain;" />', images.image.url)
        return "Aucune image principale définie dans la galerie."
    apercu_image_principale.short_description = 'Image principale de la galerie'
    
    def nb_produits(self, obj):
        return obj.produits.count()
    nb_produits.short_description = 'Nombre de produits'


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'reference', 'categorie', 'prix', 'est_en_promotion', 'est_actif', 'en_stock')
    list_filter = ('est_actif', 'en_stock', 'categorie', 'est_nouveau', 'est_meilleur_vente')
    search_fields = ('nom', 'reference', 'description', 'resume')
    list_editable = ('prix', 'est_actif', 'en_stock')
    prepopulated_fields = {'slug': ('nom', 'reference')}
    readonly_fields = ('date_creation', 'date_mise_a_jour', 'apercu_prix')
    inlines = [ImageProduitInline, CaracteristiqueProduitInline, AvisProduitInline]
    save_on_top = True
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('nom', 'slug', 'reference', 'categorie', 'description', 'resume')
        }),
        (_('Prix et stock'), {
            'fields': ('prix', 'prix_promotionnel', 'apercu_prix', 'en_stock', 'quantite')
        }),
        (_('Options d\'affichage'), {
            'fields': ('est_actif', 'est_nouveau', 'est_meilleur_vente')
        }),
        (_('SEO'), {
            'classes': ('collapse',),
            'fields': ('meta_titre', 'meta_description'),
        }),
        (_('Métadonnées'), {
            'classes': ('collapse',),
            'fields': ('date_creation', 'date_mise_a_jour', 'date_publication'),
        }),
    )
    
    def apercu_prix(self, obj):
        if obj.est_en_promotion():
            return format_html('<span style="color:red; font-weight:bold;">{} € (au lieu de {} € -{}%)</span>', 
                             obj.prix_promotionnel, obj.prix, obj.get_pourcentage_promotion())
        return f"{obj.prix} €"
    apercu_prix.short_description = 'Prix affiché'
    
    def est_en_promotion(self, obj):
        return obj.est_en_promotion()
    est_en_promotion.boolean = True
    est_en_promotion.short_description = 'Promo'


@admin.register(ImageProduit)
class ImageProduitAdmin(admin.ModelAdmin):
    list_display = ('apercu_image', 'produit', 'est_principale', 'ordre')
    list_editable = ('est_principale', 'ordre')
    list_filter = ('est_principale',)
    search_fields = ('produit__nom', 'legende')
    
    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "Aucune image"
    apercu_image.short_description = 'Image'


@admin.register(AvisProduit)
class AvisProduitAdmin(admin.ModelAdmin):
    list_display = ('produit', 'utilisateur', 'note_etoiles', 'titre', 'date_creation', 'approuve')
    list_filter = ('approuve', 'note', 'date_creation')
    search_fields = ('produit__nom', 'utilisateur__username', 'titre', 'commentaire')
    list_editable = ('approuve',)
    readonly_fields = ('date_creation', 'date_mise_a_jour')
    
    def note_etoiles(self, obj):
        return '★' * obj.note + '☆' * (5 - obj.note)
    note_etoiles.short_description = 'Note'


@admin.register(ImageCategorie)
class ImageCategorieAdmin(admin.ModelAdmin):
    list_display = ('apercu_image', 'categorie', 'legende', 'est_principale', 'ordre')
    list_filter = ('est_principale', 'categorie')
    search_fields = ('categorie__nom', 'legende')
    list_editable = ('legende', 'est_principale', 'ordre')
    readonly_fields = ('apercu_image', 'date_ajout')
    
    fieldsets = (
        (None, {
            'fields': ('categorie', 'image', 'apercu_image', 'legende', 'est_principale', 'ordre')
        }),
        (_('Métadonnées'), {
            'classes': ('collapse',),
            'fields': ('date_ajout',),
        }),
    )
    
    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100%; object-fit: contain;" />', obj.image.url)
        return "Aucune image"
    apercu_image.short_description = 'Aperçu'


@admin.register(CaracteristiqueProduit)
class CaracteristiqueProduitAdmin(admin.ModelAdmin):
    list_display = ('produit', 'nom', 'valeur', 'ordre')
    list_filter = ('produit__categorie',)
    search_fields = ('produit__nom', 'nom', 'valeur')
    list_editable = ('nom', 'valeur', 'ordre')

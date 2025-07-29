from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Categorie, Produit, ImageProduit, AvisProduit, CaracteristiqueProduit


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


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'est_active', 'nb_produits', 'apercu_image')
    list_filter = ('est_active',)
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    readonly_fields = ('date_creation', 'date_mise_a_jour', 'apercu_image')
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('nom', 'slug', 'description', 'est_active')
        }),
        (_('Image'), {
            'fields': ('image', 'apercu_image')
        }),
        (_('Métadonnées'), {
            'classes': ('collapse',),
            'fields': ('date_creation', 'date_mise_a_jour'),
        }),
    )
    
    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "Aucune image"
    apercu_image.short_description = 'Aperçu de l\'image'
    
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


@admin.register(CaracteristiqueProduit)
class CaracteristiqueProduitAdmin(admin.ModelAdmin):
    list_display = ('produit', 'nom', 'valeur', 'ordre')
    list_filter = ('produit__categorie',)
    search_fields = ('produit__nom', 'nom', 'valeur')
    list_editable = ('nom', 'valeur', 'ordre')

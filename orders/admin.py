from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Commande, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    """
    Inline pour afficher les lignes de commande dans l'interface d'administration des commandes.
    """
    model = LigneCommande
    extra = 0
    readonly_fields = ['produit', 'quantite', 'prix_unitaire', 'prix_total_display']
    fields = ['produit', 'quantite', 'prix_unitaire', 'prix_total_display']
    
    def prix_total_display(self, instance):
        return f"{instance.prix_total():.2f} €"
    prix_total_display.short_description = "Prix total"
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Commande.
    """
    list_display = [
        'id',
        'utilisateur_display',
        'date_commande',
        'statut_display',
        'montant_total_display',
        'paye_display',
        'commande_actions',
    ]
    list_filter = ['statut', 'paye', 'date_commande']
    search_fields = [
        'id',
        'utilisateur__email',
        'utilisateur__first_name',
        'utilisateur__last_name',
        'ville',
        'code_postal',
    ]
    actions = ['marquer_comme_livre', 'marquer_comme_annule']
    readonly_fields = [
        'date_commande',
        'date_mise_a_jour',
        'utilisateur_display',
        'adresse_complete',
        'montant_total_display',
    ]
    fieldsets = [
        ('Informations générales', {
            'fields': [
                'utilisateur_display',
                'date_commande',
                'date_mise_a_jour',
                'statut',
                'paye',
                'montant_total_display',
            ]
        }),
        ('Adresse de livraison', {
            'fields': [
                'adresse_complete',
            ]
        }),
    ]
    inlines = [LigneCommandeInline]
    
    def utilisateur_display(self, obj):
        """Affiche un lien vers l'utilisateur avec son nom complet."""
        url = reverse('admin:accounts_user_change', args=[obj.utilisateur.id])
        return format_html('<a href="{}">{} {}</a>', url, obj.utilisateur.first_name, obj.utilisateur.last_name or obj.utilisateur.username)
    utilisateur_display.short_description = 'Client'
    utilisateur_display.admin_order_field = 'utilisateur__last_name'
    
    def statut_display(self, obj):
        """Affiche le statut avec un code couleur."""
        colors = {
            'en_cours': 'orange',
            'livre': 'green',
            'annule': 'red',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.statut, 'black'),
            obj.get_statut_display()
        )
    statut_display.short_description = 'Statut'
    statut_display.admin_order_field = 'statut'
    
    def montant_total_display(self, obj):
        """Affiche le montant total en gras."""
        return format_html('<strong>{} €</strong>', obj.montant_total)
    montant_total_display.short_description = 'Montant total'
    
    def paye_display(self, obj):
        """Affiche l'état du paiement avec une icône."""
        if obj.paye:
            return mark_safe('<span style="color: green;">✓</span> Payé')
        return mark_safe('<span style="color: red;">✗</span> Non payé')
    paye_display.short_description = 'Paiement'
    paye_display.admin_order_field = 'paye'
    
    def adresse_complete(self, obj):
        """Affiche l'adresse complète sur plusieurs lignes."""
        return format_html(
            '{}<br>{} {}<br>{}',
            obj.adresse_livraison,
            obj.code_postal,
            obj.ville.upper(),
            obj.pays
        )
    adresse_complete.short_description = 'Adresse'
    
    def commande_actions(self, obj):
        """Affiche des boutons d'action rapide."""
        buttons = []
        if obj.statut == obj.STATUT_EN_COURS:
            buttons.append(
                f'<a class="button" href="{obj.id}/marquer-livre/">Marquer comme livré</a>'
            )
            buttons.append(
                f'<a class="button" href="{obj.id}/annuler/">Annuler la commande</a>'
            )
        return mark_safe(' '.join(buttons))
    commande_actions.short_description = 'Actions'
    commande_actions.allow_tags = True
    
    def marquer_comme_livre(self, request, queryset):
        """Action pour marquer les commandes sélectionnées comme livrées."""
        updated = 0
        for commande in queryset:
            if commande.marquer_comme_livre():
                updated += 1
        self.message_user(
            request,
            f"{updated} commande(s) marquée(s) comme livrée(s)."
        )
    marquer_comme_livre.short_description = "Marquer comme livré"
    
    def marquer_comme_annule(self, request, queryset):
        """Action pour annuler les commandes sélectionnées."""
        updated = 0
        for commande in queryset:
            if commande.annuler():
                updated += 1
        self.message_user(
            request,
            f"{updated} commande(s) annulée(s)."
        )
    marquer_comme_annule.short_description = "Annuler les commandes sélectionnées"
    
    def get_urls(self):
        """Ajoute des URLs personnalisées pour les actions rapides."""
        from django.urls import path
        
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:commande_id>/marquer-livre/',
                self.admin_site.admin_view(self.marquer_livre_view),
                name='marquer-livre',
            ),
            path(
                '<int:commande_id>/annuler/',
                self.admin_site.admin_view(self.annuler_view),
                name='annuler-commande',
            ),
        ]
        return custom_urls + urls
    
    def marquer_livre_view(self, request, commande_id, *args, **kwargs):
        """Vue pour marquer une commande comme livrée."""
        from django.shortcuts import redirect
        from django.contrib import messages
        
        try:
            commande = Commande.objects.get(id=commande_id)
            if commande.marquer_comme_livre():
                messages.success(request, f"La commande #{commande.id} a été marquée comme livrée.")
            else:
                messages.error(request, f"Impossible de marquer la commande #{commande.id} comme livrée.")
        except Commande.DoesNotExist:
            messages.error(request, "Commande introuvable.")
        
        return redirect('admin:orders_commande_changelist')
    
    def annuler_view(self, request, commande_id, *args, **kwargs):
        """Vue pour annuler une commande."""
        from django.shortcuts import redirect
        from django.contrib import messages
        
        try:
            commande = Commande.objects.get(id=commande_id)
            if commande.annuler():
                messages.success(request, f"La commande #{commande.id} a été annulée.")
            else:
                messages.error(request, f"Impossible d'annuler la commande #{commande.id}.")
        except Commande.DoesNotExist:
            messages.error(request, "Commande introuvable.")
        
        return redirect('admin:orders_commande_changelist')


@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle LigneCommande.
    """
    list_display = ['id', 'commande', 'produit', 'quantite', 'prix_unitaire', 'prix_total_display']
    list_filter = ['commande__statut']
    search_fields = ['produit__nom', 'commande__id']
    readonly_fields = ['commande', 'produit', 'quantite', 'prix_unitaire']
    
    def prix_total_display(self, obj):
        return f"{obj.prix_total():.2f} €"
    prix_total_display.short_description = "Prix total"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Ajout de CSS personnalisé pour améliorer l'interface
class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    class Media:
        css = {
            'all': ('css/admin.css',)
        }

# Remplacement du site admin par défaut
admin_site = CustomAdminSite()

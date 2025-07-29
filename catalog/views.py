from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Produit, Categorie, ImageProduit


class AccueilView(TemplateView):
    """Page d'accueil avec les produits en vedette"""
    template_name = 'catalog/accueil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produits_phares'] = Produit.objects.filter(
            est_actif=True, 
            est_meilleur_vente=True
        )[:8]
        context['nouveautes'] = Produit.objects.filter(
            est_actif=True, 
            est_nouveau=True
        )[:4]
        return context


class ListeProduitsView(ListView):
    """Liste des produits avec filtrage par catégorie"""
    model = Produit
    template_name = 'catalog/liste_produits.html'
    context_object_name = 'produits'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Produit.objects.filter(est_actif=True)
        
        # Filtrage par catégorie
        categorie_slug = self.kwargs.get('categorie_slug')
        if categorie_slug:
            self.categorie = get_object_or_404(Categorie, slug=categorie_slug, est_active=True)
            queryset = queryset.filter(categorie=self.categorie)
        else:
            self.categorie = None
        
        # Filtrage par recherche
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) | 
                Q(description__icontains=query) |
                Q(categorie__nom__icontains=query)
            )
        
        # Tri
        tri = self.request.GET.get('tri', 'date-desc')
        if tri == 'prix-asc':
            queryset = queryset.order_by('prix')
        elif tri == 'prix-desc':
            queryset = queryset.order_by('-prix')
        elif tri == 'nom-asc':
            queryset = queryset.order_by('nom')
        elif tri == 'nom-desc':
            queryset = queryset.order_by('-nom')
        else:  # date-desc par défaut
            queryset = queryset.order_by('-date_creation')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.filter(est_active=True)
        context['categorie_actuelle'] = self.categorie
        context['query'] = self.request.GET.get('q', '')
        context['tri_actuel'] = self.request.GET.get('tri', 'date-desc')
        return context


class DetailProduitView(DetailView):
    """Détail d'un produit"""
    model = Produit
    template_name = 'catalog/detail_produit.html'
    context_object_name = 'produit'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Produit.objects.filter(est_actif=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produit = self.get_object()
        
        # Produits similaires (même catégorie)
        produits_similaires = Produit.objects.filter(
            categorie=produit.categorie,
            est_actif=True
        ).exclude(id=produit.id)[:4]
        
        context['produits_similaires'] = produits_similaires
        return context


class ListeCategoriesView(ListView):
    """Liste des catégories"""
    model = Categorie
    template_name = 'catalog/liste_categories.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Categorie.objects.filter(est_active=True)


class ResultatsRechercheView(ListView):
    """Résultats de la recherche"""
    model = Produit
    template_name = 'catalog/recherche.html'
    context_object_name = 'produits'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Produit.objects.none()
            
        return Produit.objects.filter(
            Q(est_actif=True) & 
            (Q(nom__icontains=query) | 
             Q(description__icontains=query) |
             Q(categorie__nom__icontains=query))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class NouveautesView(ListView):
    """Page des nouveaux produits"""
    model = Produit
    template_name = 'catalog/nouveautes.html'
    context_object_name = 'produits'
    paginate_by = 12
    
    def get_queryset(self):
        return Produit.objects.filter(
            est_actif=True,
            est_nouveau=True
        ).order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nouveautés'
        context['page_description'] = 'Découvrez nos derniers produits ajoutés au catalogue.'
        return context


class PromotionsView(ListView):
    """Page des produits en promotion"""
    model = Produit
    template_name = 'catalog/promotions.html'
    context_object_name = 'produits'
    paginate_by = 12
    
    def get_queryset(self):
        return Produit.objects.filter(
            est_actif=True,
            prix_promotionnel__isnull=False
        ).order_by('-date_mise_a_jour')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Promotions'
        context['page_description'] = 'Profitez de nos offres spéciales et promotions en cours.'
        return context


class ContactView(TemplateView):
    """Page de contact"""
    template_name = 'catalog/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contactez-nous'
        context['page_description'] = 'Nous sommes à votre écoute pour toute question ou demande d\'information.'
        return context

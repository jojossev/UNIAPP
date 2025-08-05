from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, F, Prefetch
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from cart.models import Panier, ArticlePanier
from .models import Commande, LigneCommande
from catalog.models import Produit
from django.conf import settings


@login_required
def historique_commandes(request):
    """
    Affiche l'historique des commandes de l'utilisateur connecté avec pagination.
    """
    # Récupérer toutes les commandes de l'utilisateur
    commandes_list = Commande.objects.filter(
        utilisateur=request.user
    ).select_related('utilisateur').prefetch_related(
        Prefetch('lignes', queryset=LigneCommande.objects.select_related('produit'))
    ).order_by('-date_commande')
    
    # Pagination - 10 commandes par page
    page = request.GET.get('page', 1)
    paginator = Paginator(commandes_list, 10)
    
    try:
        commandes = paginator.page(page)
    except PageNotAnInteger:
        commandes = paginator.page(1)
    except EmptyPage:
        commandes = paginator.page(paginator.num_pages)
    
    # Calculer le montant total dépensé par l'utilisateur
    total_depense = Commande.objects.filter(
        utilisateur=request.user
    ).aggregate(total=Sum('montant_total'))['total'] or 0
    
    context = {
        'commandes': commandes,
        'total_depense': total_depense,
        'commandes_count': paginator.count,
    }
    
    return render(request, 'orders/historique.html', context)


@login_required
def detail_commande(request, commande_id):
    """
    Affiche le détail d'une commande spécifique.
    Vérifie que l'utilisateur est bien le propriétaire de la commande.
    """
    commande = get_object_or_404(
        Commande.objects.select_related('utilisateur').prefetch_related(
            Prefetch('lignes', queryset=LigneCommande.objects.select_related('produit'))
        ),
        id=commande_id,
        utilisateur=request.user
    )
    
    # Vérifier si la commande appartient bien à l'utilisateur
    if commande.utilisateur != request.user:
        messages.error(request, 'Vous n\'êtes pas autorisé à voir cette commande.')
        return redirect('orders:historique')
    
    context = {
        'commande': commande,
        'lignes_commande': commande.lignes.all(),
    }
    
    return render(request, 'orders/detail_commande.html', context)


@login_required
@require_http_methods(['POST'])
def annuler_commande(request, commande_id):
    """
    Permet à un utilisateur d'annuler sa commande si elle est encore annulable.
    N'accepte que les requêtes POST pour des raisons de sécurité.
    """
    commande = get_object_or_404(
        Commande.objects.select_related('utilisateur'),
        id=commande_id,
        utilisateur=request.user
    )
    
    if commande.annuler():
        messages.success(
            request,
            f'La commande #{commande.id} a été annulée avec succès.'
        )
    else:
        messages.error(
            request,
            'Impossible d\'annuler cette commande. Elle a peut-être déjà été traitée ou annulée.'
        )
    
    return redirect('orders:detail_commande', commande_id=commande.id)


@login_required
@require_http_methods(['GET', 'POST'])
def creer_commande(request):
    """
    Vue pour créer une nouvelle commande à partir du panier de l'utilisateur.
    """
    # Récupérer le panier de l'utilisateur
    try:
        panier = Panier.objects.get(utilisateur=request.user)
        articles = panier.items.all()
        
        # Vérifier que le panier n'est pas vide
        if not articles.exists():
            messages.warning(request, 'Votre panier est vide.')
            return redirect('cart:panier')
    except Panier.DoesNotExist:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('cart:panier')
    
    # Si c'est une requête POST, traiter la commande
    if request.method == 'POST':
        # Récupérer les informations de livraison du formulaire
        adresse_livraison = request.POST.get('adresse_livraison')
        code_postal = request.POST.get('code_postal')
        ville = request.POST.get('ville')
        pays = request.POST.get('pays')
        
        # Validation des champs requis
        if not all([adresse_livraison, code_postal, ville, pays]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('orders:creer_commande')
        
        try:
            with transaction.atomic():
                # Créer la commande
                commande = Commande.objects.create(
                    utilisateur=request.user,
                    adresse_livraison=adresse_livraison,
                    code_postal=code_postal,
                    ville=ville,
                    pays=pays,
                    montant_total=panier.total,
                    paye=True  # À remplacer par une vraie logique de paiement
                )
                
                # Vérifier le stock avant de créer la commande
                articles_avec_stock_insuffisant = []
                for article in articles:
                    if article.quantite > article.produit.quantite:
                        articles_avec_stock_insuffisant.append(
                            f"- {article.produit.nom}: {article.quantite} demandés, {article.produit.quantite} disponibles"
                        )
                
                if articles_avec_stock_insuffisant:
                    messages.error(
                        request,
                        "Stock insuffisant pour certains articles :\n" + 
                        "\n".join(articles_avec_stock_insuffisant) +
                        "\n\nVeuillez ajuster les quantités avant de réessayer."
                    )
                    return redirect('cart:panier')
                
                # Créer les lignes de commande et mettre à jour le stock
                for article in articles:
                    # Créer la ligne de commande
                    LigneCommande.objects.create(
                        commande=commande,
                        produit=article.produit,
                        quantite=article.quantite,
                        prix_unitaire=article.prix_unitaire
                    )
                    
                    # Mettre à jour le stock
                    article.produit.quantite -= article.quantite
                    if article.produit.quantite <= 0:
                        article.produit.en_stock = False
                    article.produit.save(update_fields=['quantite', 'en_stock'])
                
                # Vider le panier après la commande
                panier.items.all().delete()
                
                # Rediriger vers la page de confirmation de commande
                messages.success(request, 'Votre commande a été passée avec succès !')
                return redirect('orders:detail_commande', commande_id=commande.id)
                
        except Exception as e:
            # En cas d'erreur, annuler la transaction et afficher un message d'erreur
            if settings.DEBUG:
                print(f"Erreur lors de la création de la commande : {str(e)}")
            messages.error(
                request,
                'Une erreur est survenue lors de la création de votre commande. Veuillez réessayer.'
            )
            return redirect('cart:panier')
    
    # Si c'est une requête GET, afficher le formulaire de commande
    context = {
        'panier': panier,
        'articles': articles,
        'total': panier.total,
    }
    return render(request, 'orders/creer_commande.html', context)

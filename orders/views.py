from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, F
from django.http import JsonResponse
from .models import Commande

@login_required
def historique_commandes(request):
    """
    Affiche l'historique des commandes de l'utilisateur connecté.
    """
    commandes = Commande.objects.filter(
        utilisateur=request.user
    ).order_by('-date_commande')
    
    # Calculer le montant total dépensé par l'utilisateur
    total_depense = commandes.aggregate(
        total=Sum('montant_total')
    )['total'] or 0
    
    context = {
        'commandes': commandes,
        'total_depense': total_depense,
        'commandes_count': commandes.count(),
    }
    
    return render(request, 'orders/historique.html', context)


@login_required
def detail_commande(request, commande_id):
    """
    Affiche le détail d'une commande spécifique.
    Vérifie que l'utilisateur est bien le propriétaire de la commande.
    """
    commande = get_object_or_404(
        Commande.objects.select_related('utilisateur').prefetch_related('lignes__produit'),
        id=commande_id,
        utilisateur=request.user
    )
    
    context = {
        'commande': commande,
        'lignes_commande': commande.lignes.all(),
    }
    
    return render(request, 'orders/detail_commande.html', context)


@login_required
def annuler_commande(request, commande_id):
    """
    Permet à un utilisateur d'annuler sa commande si elle est encore annulable.
    """
    if request.method == 'POST':
        commande = get_object_or_404(
            Commande,
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
    
    return redirect('orders:historique')

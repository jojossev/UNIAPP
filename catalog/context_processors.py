from .models import Categorie

def categories(request):
    """Ajoute la liste des catégories actives au contexte de tous les templates."""
    return {
        'categories': Categorie.objects.filter(est_active=True).order_by('nom')
    }

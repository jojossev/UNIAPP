import os
import sys
from django.http import HttpResponse, JsonResponse
from django.conf import settings

def handler(request, *args, **kwargs):
    try:
        # Configuration minimale pour Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
        
        # Importer Django après avoir défini les variables d'environnement
        import django
        django.setup()
        
        # Réponse de test simple
        return HttpResponse(
            "Bienvenue sur l'application Django!\n\n"
            f"Python: {sys.version}\n"
            f"Django: {django.get_version()}\n"
            f"Chemin: {os.getcwd()}",
            content_type="text/plain"
        )
        
    except Exception as e:
        # En cas d'erreur, renvoyer les détails pour le débogage
        import traceback
        error_msg = f"Erreur: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        return HttpResponse(error_msg, status=500, content_type="text/plain")

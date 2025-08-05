from http.server import BaseHTTPRequestHandler
import os
import sys
import json

# Classe de base pour le gestionnaire Vercel
class VercelRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Configuration minimale pour Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
            
            # Importer Django après avoir défini les variables d'environnement
            import django
            django.setup()
            from django.http import HttpResponse
            
            # Réponse de test simple
            response = HttpResponse(
                "Bienvenue sur l'application Django!\n\n"
                f"Python: {sys.version}\n"
                f"Django: {django.get_version()}\n"
                f"Chemin: {os.getcwd()}",
                content_type="text/plain"
            )
            
            # Envoyer la réponse
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            # En cas d'erreur, renvoyer les détails pour le débogage
            import traceback
            error_msg = f"Erreur: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(error_msg.encode('utf-8'))

# Fonction de gestionnaire requise par Vercel
def handler(request, context=None):
    return VercelRequestHandler(request, context, None)

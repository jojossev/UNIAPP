import os
import sys
import locale

class CharsetMiddleware:
    """
    Middleware pour forcer l'encodage UTF-8 sur toutes les réponses HTTP.
    Gère également la configuration de l'encodage système.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuration de l'encodage système
        if sys.version_info[0] < 3:
            reload(sys)
            sys.setdefaultencoding('utf-8')
        
        # Forcer l'encodage de la locale
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        
        # Configuration de l'environnement pour l'encodage
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')

    def __call__(self, request):
        # Traitement de la requête
        response = self.get_response(request)
        
        # Définir l'encodage du contenu sur UTF-8
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type and 'charset=' not in content_type:
            response['Content-Type'] = content_type + '; charset=utf-8'
        elif not content_type:
            response['Content-Type'] = 'text/html; charset=utf-8'
            
        # Définir l'en-tête Content-Encoding si nécessaire
        if 'Content-Encoding' not in response:
            response['Content-Encoding'] = 'utf-8'
            
        return response

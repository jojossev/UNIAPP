from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai import reco, chatbot, image_search, history, descgen, smartsearch, sentiment, filtering, review_summary
from ai.translate import translate as translate_text

@csrf_exempt
def recommendation_view(request):
    """
    Endpoint IA : recommandations personnalisées (mock)
    """
    user_id = request.GET.get('user_id')
    recos = reco.get_recommendations(user_id=user_id)
    return JsonResponse({'recommendations': recos})

@csrf_exempt
def chatbot_view(request):
    """
    Endpoint IA : chatbot IA (mock)
    """
    try:
        # Vérifier la méthode HTTP
        if request.method != 'POST':
            return JsonResponse(
                {'error': 'Méthode non autorisée'}, 
                status=405
            )
        
        # Vérifier si le contenu est du JSON
        if request.content_type != 'application/json':
            return JsonResponse(
                {'error': 'Content-Type doit être application/json'}, 
                status=400
            )
        
        # Essayer de parser le JSON
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Corps de requête JSON invalide'}, 
                status=400
            )
        
        # Récupérer la question
        question = data.get('question', '').strip()
        if not question:
            return JsonResponse(
                {'error': 'Le champ "question" est requis'}, 
                status=400
            )
        
        # Obtenir une réponse du chatbot
        try:
            answer = chatbot.ask_bot(question)
            if not answer:
                raise ValueError("Aucune réponse du moteur d'IA")
                
            return JsonResponse({
                'answer': answer,
                'status': 'success'
            })
            
        except Exception as e:
            print(f"Erreur du chatbot: {str(e)}", file=sys.stderr)
            return JsonResponse({
                'error': f'Erreur lors du traitement de la requête: {str(e)}',
                'status': 'error'
            }, status=500)
            
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}", file=sys.stderr)
        return JsonResponse({
            'error': 'Une erreur inattendue est survenue',
            'status': 'error'
        }, status=500)

@csrf_exempt
def image_search_view(request):
    """
    Endpoint IA : recherche de produits par image (mock)
    """
    # Pour démo, on ne traite pas de vraie image ici
    return JsonResponse({'results': image_search.search_by_image(None)})

@csrf_exempt
def history_view(request):
    """
    Endpoint IA : suggestions selon historique (mock)
    """
    user_id = request.GET.get('user_id')
    # Ici, on simule un historique vide
    suggestions = history.suggest_from_history(user_id, history=None)
    return JsonResponse({'suggestions': suggestions})

@csrf_exempt
def descgen_view(request):
    """
    Endpoint IA : génération automatique de description produit (mock)
    """
    nom = request.GET.get('nom', 'Produit')
    desc = descgen.generate_description(nom)
    return JsonResponse({'description': desc})

@csrf_exempt
def translate_view(request):
    """
    Endpoint IA : traduction automatique
    """
    try:
        # Vérifier la méthode HTTP
        if request.method not in ['GET', 'POST']:
            return JsonResponse(
                {'error': 'Méthode non autorisée'}, 
                status=405
            )
        
        # Récupérer les paramètres de la requête
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('utf-8'))
                text = data.get('text', '')
                target_lang = data.get('target_lang', 'en')
                source_lang = data.get('source_lang', 'auto')
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'Corps de requête JSON invalide'}, 
                    status=400
                )
        else:  # GET
            text = request.GET.get('text', '')
            target_lang = request.GET.get('lang', 'en')
            source_lang = request.GET.get('source', 'auto')
        
        if not text:
            return JsonResponse(
                {'error': 'Le texte à traduire est requis'}, 
                status=400
            )
        
        # Appeler le service de traduction
        translated_text = translate_text(
            text, 
            target_lang=target_lang
        )
        
        # Enregistrer l'historique de traduction si l'utilisateur est connecté
        if request.user.is_authenticated:
            from .models import TranslationHistory
            
            # Créer une entrée d'historique
            TranslationHistory.objects.create(
                user=request.user,
                source_language=source_lang,
                target_language=target_lang,
                original_text=text,
                translated_text=translated_text
            )
        
        # Retourner la réponse
        return JsonResponse({
            'status': 'success',
            'original_text': text,
            'translated_text': translated_text,
            'source_language': source_lang,
            'target_language': target_lang
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@csrf_exempt
def smartsearch_view(request):
    """
    Endpoint IA : recherche intelligente (mock)
    """
    query = request.GET.get('query', '')
    results = smartsearch.smart_search(query)
    return JsonResponse({'results': results})

@csrf_exempt
def sentiment_view(request):
    """
    Endpoint IA : analyse de sentiment (mock)
    """
    text = request.GET.get('text', '')
    result = sentiment.analyze_sentiment(text)
    return JsonResponse(result)

@csrf_exempt
def filtering_view(request):
    """
    Endpoint IA : filtrage intelligent (mock)
    """
    # On simule une liste produits
    products = [
        {'id': 1, 'nom': 'Produit X'},
        {'id': 2, 'nom': 'Produit Y'},
        {'id': 3, 'nom': 'Produit Z'},
    ]
    preferences = {}
    filtered = filtering.filter_products(products, preferences)
    return JsonResponse({'filtered': filtered})

@csrf_exempt
@csrf_exempt
def review_summary_view(request):
    """
    Endpoint IA : résumé des avis clients (mock)
    """
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        summary = review_summary.generate_summary(product_id=product_id)
        return JsonResponse({'summary': summary})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def suggestions_view(request):
    """
    Endpoint IA : suggestions personnalisées basées sur l'historique de l'utilisateur
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Début de la vue suggestions_view")
        
        if not request.user.is_authenticated:
            logger.warning("Utilisateur non authentifié")
            return JsonResponse({'error': 'Utilisateur non authentifié'}, status=401)
        
        # Récupérer l'historique de l'utilisateur (simulé)
        user_id = request.user.id
        logger.info(f"Récupération des suggestions pour l'utilisateur {user_id}")
        
        # Appel à la fonction get_suggestions avec logging
        try:
            suggestions = history.get_suggestions(user_id=user_id)
            logger.info(f"Suggestions récupérées: {len(suggestions) if suggestions else 0} suggestions")
            if suggestions:
                logger.debug(f"Première suggestion: {suggestions[0]}")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à get_suggestions: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Erreur lors de la récupération des suggestions'}, status=500)
        
        # Rendre le template partiel avec les suggestions
        try:
            logger.info("Rendu du template partiel")
            html = render_to_string('ai_user/suggestions_partial.html', 
                                 {'suggestions': suggestions or []})
            logger.debug("Template rendu avec succès")
            return HttpResponse(html)
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu du template: {str(e)}", exc_info=True)
            return JsonResponse(
                {'error': 'Erreur lors de la génération des suggestions'}, 
                status=500
            )
            
    except Exception as e:
        logger.critical(f"Erreur inattendue dans suggestions_view: {str(e)}", exc_info=True)
        return JsonResponse(
            {'error': 'Une erreur inattendue est survenue'}, 
            status=500
        )

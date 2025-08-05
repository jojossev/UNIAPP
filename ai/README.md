# IA Utilisateur – E-commerce Django

Ce dossier contient les modules et endpoints pour toutes les fonctionnalités IA côté utilisateur.

## Fonctionnalités prévues
- Recommandation de produits personnalisée
- Chatbot IA pour assistance client
- Recherche de produits par image
- Suggestions automatiques selon historique de navigation
- Générateur automatique de descriptions de produits
- Traduction automatique des descriptions (multilingue)
- Recherche intelligente (correction orthographique, synonymes, etc.)
- Analyse de sentiment des avis clients
- Filtrage intelligent selon préférences d'achat
- Résumé automatique des avis clients

## Structure proposée
- `reco.py` : recommandations personnalisées
- `chatbot.py` : assistant IA
- `image_search.py` : recherche par image
- `history.py` : suggestions selon navigation
- `descgen.py` : génération de descriptions
- `translate.py` : traduction automatique
- `smartsearch.py` : recherche intelligente
- `sentiment.py` : analyse de sentiment
- `filtering.py` : filtrage intelligent
- `review_summary.py` : résumé des avis

Chaque module expose :
- une fonction principale
- un endpoint Django REST (à brancher sur l’API ou les vues)
- une version “mock” (pour tests sans API clé)

## Pré-requis
- Python 3.10+
- Django REST Framework
- (optionnel) : clés API OpenAI, HuggingFace, DeepL, Recombee, etc.

---

**Pour activer une fonctionnalité :**
1. Branche le module correspondant dans la vue Django (ou via AJAX/JS côté front)
2. Fournis les clés API si besoin
3. Personnalise le template HTML pour afficher le résultat IA

---

Contact : équipe IA

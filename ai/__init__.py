"""
Module d'intégration IA pour l'application e-commerce
"""
from .reco import get_recommendations
from .chatbot import ask_bot
from .image_search import search_by_image
from .history import get_suggestions, suggest_from_history
from .descgen import generate_description
from .translate import translate
from .smartsearch import smart_search
from .sentiment import analyze_sentiment
from .filtering import filter_products
from .review_summary import summarize_reviews

__all__ = [
    'get_recommendations',
    'ask_bot',
    'search_by_image',
    'get_suggestions',
    'suggest_from_history',
    'generate_description',
    'translate',
    'smart_search',
    'analyze_sentiment',
    'filter_products',
    'summarize_reviews'
]

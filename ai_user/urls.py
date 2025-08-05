from django.urls import path
from . import views

urlpatterns = [
    path('reco/', views.recommendation_view, name='ai_recommendation'),
    path('chatbot/', views.chatbot_view, name='ai_chatbot'),
    path('image_search/', views.image_search_view, name='ai_image_search'),
    path('history/', views.history_view, name='ai_history'),
    path('descgen/', views.descgen_view, name='ai_descgen'),
    path('translate/', views.translate_view, name='ai_translate'),
    path('smartsearch/', views.smartsearch_view, name='ai_smartsearch'),
    path('sentiment/', views.sentiment_view, name='ai_sentiment'),
    path('filtering/', views.filtering_view, name='ai_filtering'),
    path('review_summary/', views.review_summary_view, name='ai_review_summary'),
    path('suggestions/', views.suggestions_view, name='ai_suggestions'),
]

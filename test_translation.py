from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class TranslationAPITest(TestCase):
    def setUp(self):
        # Créer un utilisateur de test
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        
        # URL de l'API de traduction (utiliser reverse pour obtenir l'URL)
        self.translate_url = reverse('ai_translate')
    
    def test_authenticated_translation(self):
        """Test de traduction avec un utilisateur authentifié"""
        # Se connecter avec l'utilisateur de test
        self.client.force_login(self.user)
        
        # Données de la requête
        data = {
            'text': 'Hello, how are you?',
            'target_lang': 'fr',
            'source_lang': 'en'
        }
        
        # Effectuer une requête POST simple
        response = self.client.post(
            self.translate_url,
            data=data
        )
        
        # Vérifier que la réponse est un succès
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la réponse contient les champs attendus
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('translated_text', response_data)

if __name__ == '__main__':
    import unittest
    unittest.main()

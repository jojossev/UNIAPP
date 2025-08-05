"""
Module de chatbot IA pour l'assistance client
"""
import random
from datetime import datetime

# Réponses prédéfinies pour différentes intentions
RESPONSES = {
    'greeting': [
        "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
        'Salut ! En quoi puis-je vous assister ?',
        'Bienvenue ! Comment puis-je vous être utile ?'
    ],
    'thanks': [
        'Je vous en prie ! Avez-vous d\'autres questions ?',
        'Avec plaisir ! N\'hésitez pas si vous avez besoin d\'aide.',
        'De rien ! Comment puis-je vous aider davantage ?'
    ],
    'goodbye': [
        'Au revoir ! Passez une excellente journée !',
        'À bientôt ! N\'hésitez pas à revenir si vous avez des questions.',
        'Merci de votre visite ! À la prochaine !'
    ],
    'help': [
        'Je peux vous aider à trouver des produits, suivre vos commandes, ou répondre à vos questions sur nos services.',
        'Je peux vous assister pour la recherche de produits, le suivi de commande, ou toute question sur notre site.',
        'Comment puis-je vous aider ? Je peux vous guider dans vos achats ou répondre à vos questions.'
    ],
    'fallback': [
        'Je ne suis pas sûr de bien comprendre. Pourriez-vous reformuler votre question ?',
        'Désolé, je n\'ai pas saisi votre demande. Pouvez-vous préciser ?',
        'Je ne suis pas certain de pouvoir répondre à cette question. Voulez-vous essayer de la formuler autrement ?'
    ]
}

def detect_intent(question):
    """Détecte l'intention derrière la question de l'utilisateur"""
    question = question.lower()
    
    if any(word in question for word in ['bonjour', 'salut', 'coucou', 'hey', 'hello']):
        return 'greeting'
    elif any(word in question for word in ['merci', 'remercie', 'super', 'parfait', 'génial']):
        return 'thanks'
    elif any(word in question for word in ['au revoir', 'à plus', 'bye', 'a+', 'ciao']):
        return 'goodbye'
    elif any(word in question for word in ['aide', 'aider', 'peux-tu m\'aider', 'comment faire']):
        return 'help'
    
    return None

def get_product_info(question):
    """Simule la récupération d'informations sur un produit"""
    # Dans une vraie implémentation, on interrogerait ici la base de données
    products = {
        'ordinateur': 'Nous avons plusieurs ordinateurs portables et de bureau disponibles. Souhaitez-vous des conseils pour choisir ?',
        'téléphone': 'Nous proposons les dernières marques de smartphones. Avez-vous une marque ou un modèle précis en tête ?',
        'livre': 'Notre sélection de livres couvre divers genres. Quel type de livre recherchez-vous ?',
    }
    
    question = question.lower()
    for product, response in products.items():
        if product in question:
            return response
    
    return None

def get_order_status(question):
    """Simule la vérification du statut d'une commande"""
    if any(word in question.lower() for word in ['commande', 'colis', 'livraison', 'suivi']):
        return "Pour vérifier le statut de votre commande, veuillez vous connecter à votre compte ou utiliser le numéro de suivi reçu par email."
    return None

def ask_bot(question, user_id=None):
    """
    Génère une réponse du chatbot IA basée sur la question de l'utilisateur.
    
    Args:
        question (str): La question ou le message de l'utilisateur
        user_id (str, optional): L'identifiant de l'utilisateur pour personnaliser la réponse
        
    Returns:
        str: La réponse du chatbot
    """
    if not question or not isinstance(question, str):
        return "Je n'ai pas compris votre demande. Pouvez-vous reformuler ?"
    
    # Détecter l'intention
    intent = detect_intent(question)
    
    # Répondre selon l'intention détectée
    if intent and intent in RESPONSES:
        return random.choice(RESPONSES[intent])
    
    # Vérifier les questions sur les produits
    product_response = get_product_info(question)
    if product_response:
        return product_response
    
    # Vérifier les questions sur le statut des commandes
    order_response = get_order_status(question)
    if order_response:
        return order_response
    
    # Réponse par défaut si aucune intention spécifique n'est détectée
    default_responses = [
        "Je peux vous aider à trouver des produits, vérifier le statut d'une commande, ou répondre à vos questions sur nos services.",
        "Je suis là pour vous aider avec vos achats. Que souhaitez-vous savoir ?",
        "Je peux vous assister pour la recherche de produits ou répondre à vos questions. Comment puis-je vous aider ?"
    ]
    
    # Si l'utilisateur pose une question directe
    if '?' in question:
        return random.choice([
            "Je ne suis pas certain de pouvoir répondre à cette question. Voulez-vous que je vous mette en contact avec notre service client ?",
            "C'est une excellente question. Pour une réponse précise, je vous recommande de contacter notre service client.",
            "Je ne dispose pas de cette information pour le moment. Souhaitez-vous que je recherche cela pour vous ?"
        ])
    
    return random.choice(default_responses)

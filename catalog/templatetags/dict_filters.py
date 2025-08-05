from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtre personnalisé pour accéder à une valeur de dictionnaire par clé dans un template.
    
    Exemple d'utilisation dans le template :
    {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key, 0)  # Retourne 0 par défaut si la clé n'existe pas

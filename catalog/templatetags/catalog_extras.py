from django import template

print("Chargement de catalog_extras.py...")  # Message de débogage

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
    return dictionary.get(key)

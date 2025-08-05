from .cart import Cart

def cart(request):
    """
    Context processor qui ajoute le panier au contexte de tous les templates.
    Permet d'accéder au panier depuis n'importe quelle vue sans avoir à le passer explicitement.
    """
    return {'cart': Cart(request)}

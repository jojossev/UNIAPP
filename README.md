# E-commerce Django

Application de vente en ligne développée avec Django.

## Fonctionnalités

### Module d'Authentification
- Inscription avec email et mot de passe
- Connexion/Déconnexion sécurisée
- Réinitialisation du mot de passe
- Gestion du profil utilisateur
- Changement de mot de passe

### Module Catalogue
- Affichage des produits par catégorie
- Fiches produits détaillées
- Système de recherche
- Pages spéciales : Nouveautés, Promotions

### Module Panier
- Ajout/Suppression de produits
- Mise à jour des quantités
- Calcul automatique des totaux
- Affichage dynamique du nombre d'articles
- API AJAX pour les mises à jour en temps réel

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (pour cloner le dépôt)

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone [URL_DU_DEPOT]
   cd ecommerce-django
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   # Sur Windows :
   .\venv\Scripts\activate
   # Sur macOS/Linux :
   # source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Effectuer les migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Créer un superutilisateur (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

7. **Accéder à l'application**
   - Site web : http://127.0.0.1:8000/
   - Interface d'administration : http://127.0.0.1:8000/admin/

## Structure du projet

ecommerce/
├── accounts/                  # Application d'authentification
│   ├── migrations/           # Fichiers de migration
│   ├── templates/            # Templates spécifiques à l'application
│   ├── __init__.py
│   ├── admin.py             # Configuration de l'interface admin
│   ├── apps.py              # Configuration de l'application
│   ├── forms.py             # Formulaires personnalisés
│   ├── models.py            # Modèles de données
│   ├── urls.py              # URLs de l'application
│   └── views.py             # Vues de l'application
├── cart/                     # Application panier
│   ├── migrations/          # Fichiers de migration
│   ├── templates/           # Templates du panier
│   ├── __init__.py
│   ├── admin.py            # Configuration admin
│   ├── apps.py             # Configuration de l'application
│   ├── models.py           # Modèles Panier et ArticlePanier
│   ├── urls.py             # URLs du panier
│   └── views.py            # Vues du panier
├── catalog/                 # Application catalogue
│   ├── migrations/         # Fichiers de migration
│   ├── static/             # Fichiers statiques spécifiques
│   ├── templates/          # Templates du catalogue
│   ├── __init__.py
│   ├── admin.py           # Configuration admin
│   ├── apps.py            # Configuration de l'application
│   ├── context_processors.py # Processeurs de contexte
│   ├── models.py          # Modèles Produit, Catégorie, etc.
│   ├── urls.py           # URLs du catalogue
│   └── views.py          # Vues du catalogue
├── ecommerce/               # Configuration du projet
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # Paramètres du projet
│   ├── urls.py              # URLs principaux
│   └── wsgi.py
├── static/                  # Fichiers statiques (CSS, JS, images)
│   ├── css/
│   │   ├── style.css       # Styles généraux
│   │   └── catalog.css     # Styles spécifiques au catalogue
│   └── js/
│       └── main.js         # JavaScript principal
├── templates/               # Templates globaux
│   ├── base.html           # Template de base principal
│   └── includes/           # Partiels réutilisables
│       └── header.html     # En-tête du site
├── .gitignore
├── manage.py               # Script de gestion Django
├── requirements.txt        # Dépendances du projet
└── README.md               # Ce fichier

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
DEBUG=True
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@example.com
```

### Configuration de l'email (en production)

Pour configurer l'envoi d'emails en production, modifiez les paramètres suivants dans `settings.py` :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'votre_serveur_smtp'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre_email@example.com'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'
```

## Déploiement

Ce projet peut être déployé sur différentes plateformes :

- **Heroku**
- **PythonAnywhere**
- **VPS** avec Nginx et Gunicorn

Consultez la documentation de Django pour plus d'informations sur le déploiement : [Déploiement Django](https://docs.djangoproject.com/fr/4.2/howto/deployment/)

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Auteur

- [Votre Nom](https://github.com/votrepseudo)

## Remerciements

- [Django](https://www.djangoproject.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Django Crispy Forms](https://django-crispy-forms.readthedocs.io/)

---

*Dernière mise à jour : Juillet 2025*

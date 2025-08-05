import os
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm

# Configuration du logger
logger = logging.getLogger(__name__)
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.role = 'client'  # Par défaut, tous les nouveaux utilisateurs sont des clients
                user.save()
                messages.success(request, 'Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.')
                return redirect('accounts:login')  # Correction du nom de l'URL
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de la création du compte : {str(e)}")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenue, {user.username} !')
            return redirect('catalog:accueil')  # Redirection vers la page d'accueil du catalogue
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('catalog:accueil')  # Redirection vers la page d'accueil du catalogue


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = UserProfileForm(
            data=request.POST, 
            files=request.FILES, 
            instance=request.user
        )
        
        if form.is_valid():
            try:
                user = form.save(commit=False)
                
                # Si une nouvelle image de profil est fournie
                if 'profile_picture' in request.FILES:
                    try:
                        logger.info(f"Tentative de mise à jour de la photo de profil pour l'utilisateur {request.user.username}")
                        
                        # Créer le répertoire de destination s'il n'existe pas
                        upload_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pics', f'user_{request.user.id}')
                        os.makedirs(upload_dir, exist_ok=True)
                        logger.info(f"Répertoire de destination : {upload_dir}")
                        
                        # Vérifier les permissions du répertoire
                        if not os.access(upload_dir, os.W_OK):
                            error_msg = f"Le répertoire {upload_dir} n'est pas accessible en écriture"
                            logger.error(error_msg)
                            if is_ajax:
                                return JsonResponse({
                                    'success': False,
                                    'message': error_msg,
                                    'error': 'Erreur de permissions sur le répertoire de destination'
                                }, status=500)
                            messages.error(request, error_msg)
                            return redirect('accounts:profile')
                        
                        # Supprimer l'ancienne image si elle existe
                        if request.user.profile_picture:
                            try:
                                old_picture = request.user.profile_picture
                                if old_picture and os.path.isfile(old_picture.path):
                                    logger.info(f"Suppression de l'ancienne photo : {old_picture.path}")
                                    os.remove(old_picture.path)
                            except Exception as e:
                                logger.error(f"Erreur lors de la suppression de l'ancienne photo : {str(e)}")
                                # Ne pas bloquer la suite si la suppression échoue
                        
                        # Mettre à jour le champ profile_picture
                        uploaded_file = request.FILES['profile_picture']
                        logger.info(f"Nouveau fichier reçu : {uploaded_file.name} ({uploaded_file.size} octets)")
                        user.profile_picture = uploaded_file
                    
                    except Exception as e:
                        import traceback
                        error_details = traceback.format_exc()
                        logger.error(f"Erreur lors de la mise à jour du profil : {str(e)}\n{error_details}")
                        
                        error_message = f"Une erreur est survenue lors de la mise à jour de votre photo de profil."
                        if is_ajax:
                            return JsonResponse({
                                'success': False,
                                'message': error_message,
                                'error': str(e),
                                'details': str(error_details) if settings.DEBUG else None
                            }, status=500)
                        
                        messages.error(request, error_message)
                        if settings.DEBUG:
                            messages.error(request, f"Détails : {str(e)}")
                
                # Sauvegarder l'utilisateur
                user.save()
                
                # Préparer la réponse
                response_data = {
                    'success': True,
                    'message': 'Votre photo de profil a été mise à jour avec succès !',
                }
                
                # Ajouter l'URL de l'image si elle existe
                if user.profile_picture:
                    response_data['profile_picture_url'] = user.profile_picture.url
                
                # Si c'est une requête AJAX, renvoyer la réponse JSON
                if is_ajax:
                    return JsonResponse(response_data)
                
                # Sinon, ajouter un message et rediriger
                messages.success(request, response_data['message'])
                return redirect('accounts:profile')
                
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de la mise à jour de votre profil : {str(e)}")
        else:
            # Le formulaire n'est pas valide
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Veuillez corriger les erreurs ci-dessous.'
                }, status=400)
            
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        # Méthode GET
        form = UserProfileForm(instance=request.user)
    
    # Si c'est une requête AJAX GET, renvoyer les données du profil en JSON
    if is_ajax and request.method == 'GET':
        return JsonResponse({
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'profile_picture_url': request.user.profile_picture.url if hasattr(request.user, 'profile_picture') and request.user.profile_picture else None
        })
    
    # Pour une requête normale, afficher le template
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
    })


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/password_reset/done/'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/reset/done/'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

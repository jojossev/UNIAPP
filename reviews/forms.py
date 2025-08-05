from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Review

class ReviewForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier un avis sur un produit.
    """
    class Meta:
        model = Review
        fields = ['title', 'rating', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Titre de votre avis'),
                'maxlength': '200',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Détaillez votre expérience avec ce produit'),
                'rows': 5,
                'maxlength': '2000',
            }),
            'rating': forms.RadioSelect(
                choices=Review.RATING_CHOICES,
                attrs={
                    'class': 'rating-radio',
                }
            ),
        }
        labels = {
            'title': _('Titre'),
            'rating': _('Note'),
            'comment': _('Commentaire'),
        }
        help_texts = {
            'rating': _('Sélectionnez une note de 1 à 5 étoiles'),
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Personnalisation du widget de notation
        self.fields['rating'].widget.attrs.update({
            'class': 'rating-input',
            'min': 1,
            'max': 5,
            'step': 1,
        })
    
    def clean_rating(self):
        """Valide que la note est comprise entre 1 et 5."""
        rating = self.cleaned_data.get('rating')
        if rating not in dict(Review.RATING_CHOICES).keys():
            raise ValidationError(_('Veuillez sélectionner une note valide.'))
        return rating
    
    def clean(self):
        """Validation supplémentaire pour s'assurer que l'utilisateur n'a pas déjà laissé un avis."""
        cleaned_data = super().clean()
        
        if self.instance._state.adding and self.user and self.product:
            # Vérification si l'utilisateur a déjà laissé un avis pour ce produit
            if Review.objects.filter(user=self.user, product=self.product).exists():
                raise ValidationError({
                    'user': _('Vous avez déjà laissé un avis pour ce produit.')
                })
        
        return cleaned_data


class ReviewEditForm(ReviewForm):
    """
    Formulaire pour modifier un avis existant.
    Permet de modifier uniquement certains champs.
    """
    class Meta(ReviewForm.Meta):
        fields = ['title', 'rating', 'comment']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ne pas vérifier la contrainte d'unicité lors de la modification
        self.fields['rating'].required = True
    
    def clean(self):
        """Sauter la validation d'unicité pour l'édition."""
        return super(forms.ModelForm, self).clean()

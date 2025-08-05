from django import forms
from .models import AvisProduit

class AvisProduitForm(forms.ModelForm):
    class Meta:
        model = AvisProduit
        fields = ['note', 'titre', 'commentaire']
        widgets = {
            'note': forms.RadioSelect(choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)]),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Titre de l'avis"}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Votre commentaire...", 'rows': 4}),
        }

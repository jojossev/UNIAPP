from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Produit, AvisProduit
from .forms import AvisProduitForm

@method_decorator(login_required, name='dispatch')
class AvisProduitCreateView(CreateView):
    model = AvisProduit
    form_class = AvisProduitForm
    template_name = 'catalog/avis_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.produit = get_object_or_404(Produit, slug=kwargs['slug'], est_actif=True)
        # Vérifier que l'utilisateur a acheté le produit
        if not self.produit.has_purchased_by_user(request.user):
            messages.error(request, "Vous devez avoir acheté ce produit pour laisser un avis.")
            return redirect(self.produit.get_absolute_url())
        # Vérifier que l'utilisateur n'a pas déjà laissé un avis
        if AvisProduit.objects.filter(produit=self.produit, utilisateur=request.user).exists():
            messages.warning(request, "Vous avez déjà laissé un avis pour ce produit.")
            return redirect(self.produit.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.produit = self.produit
        form.instance.utilisateur = self.request.user
        # Optionnel : avis en attente de modération
        form.instance.approuve = False
        messages.success(self.request, "Votre avis a été soumis et sera publié après modération.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.produit.get_absolute_url()

@method_decorator(login_required, name='dispatch')
class AvisProduitUpdateView(UpdateView):
    model = AvisProduit
    form_class = AvisProduitForm
    template_name = 'catalog/avis_form.html'

    def get_queryset(self):
        # L'utilisateur ne peut modifier que son propre avis
        return AvisProduit.objects.filter(utilisateur=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        avis = self.get_object()
        if avis.produit.has_purchased_by_user(request.user) is False:
            messages.error(request, "Vous ne pouvez modifier un avis que pour un produit acheté.")
            return redirect(avis.produit.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.produit.get_absolute_url()

@method_decorator(login_required, name='dispatch')
class AvisProduitDeleteView(DeleteView):
    model = AvisProduit
    template_name = 'catalog/avis_confirm_delete.html'

    def get_queryset(self):
        # L'utilisateur ne peut supprimer que son propre avis
        return AvisProduit.objects.filter(utilisateur=self.request.user)

    def get_success_url(self):
        return self.object.produit.get_absolute_url()

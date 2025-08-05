from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count

from catalog.models import Produit as Product
from .models import Review
from .forms import ReviewForm, ReviewEditForm


class ProductReviewListView(ListView):
    """
    Affiche la liste des avis pour un produit donné.
    """
    model = Review
    template_name = 'reviews/product_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 5
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, pk=self.kwargs['product_id'], is_active=True)
        return Review.objects.filter(
            product=self.product, 
            is_approved=True
        ).select_related('user').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        
        # Statistiques des notes
        stats = Review.objects.filter(
            product=self.product, 
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        context.update({
            'avg_rating': round(stats['avg_rating'] or 0, 1),
            'total_reviews': stats['total_reviews'],
            'rating_distribution': self.get_rating_distribution(),
        })
        
        # Vérifier si l'utilisateur peut laisser un avis
        if self.request.user.is_authenticated:
            context['user_review'] = Review.objects.filter(
                user=self.request.user, 
                product=self.product
            ).first()
        
        return context
    
    def get_rating_distribution(self):
        """Retourne la distribution des notes pour ce produit."""
        from django.db.models import Count, F
        
        distribution = Review.objects.filter(
            product=self.product, 
            is_approved=True
        ).values('rating').annotate(
            count=Count('id'),
            percentage=Count('id') * 100 / F('product__review_count')
        ).order_by('-rating')
        
        # Créer un dictionnaire avec toutes les notes de 1 à 5
        rating_distribution = {i: 0 for i in range(5, 0, -1)}
        
        for item in distribution:
            rating_distribution[item['rating']] = {
                'count': item['count'],
                'percentage': round(item['percentage'], 1) if item['percentage'] else 0
            }
            
        return rating_distribution


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer un nouvel avis sur un produit.
    """
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['product_id'], is_active=True)
        
        # Vérifier si l'utilisateur est connecté
        if not request.user.is_authenticated:
            messages.warning(request, _('Vous devez être connecté pour laisser un avis.'))
            return redirect('account_login') + f'?next={request.path}'
            
        # Vérifier si l'utilisateur a déjà laissé un avis pour ce produit
        existing_review = Review.objects.filter(
            user=request.user, 
            product=self.product
        ).first()
        
        if existing_review:
            messages.info(request, _('Vous avez déjà laissé un avis pour ce produit.'))
            return redirect('reviews:review_edit', review_id=existing_review.id)
            
        # Vérifier si l'utilisateur a acheté le produit (sauf pour les administrateurs)
        if not request.user.is_staff and not self.product.has_purchased_by_user(request.user):
            messages.warning(
                request, 
                _('Seuls les clients ayant acheté ce produit peuvent laisser un avis.')
            )
            return redirect(self.product.get_absolute_url())
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        context['has_purchased'] = self.product.has_purchased_by_user(self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = self.product
        form.instance.is_purchased = self.product.has_purchased_by_user(self.request.user)
        
        response = super().form_valid(form)
        messages.success(self.request, _('Votre avis a été enregistré avec succès !'))
        
        return response
    
    def get_success_url(self):
        return reverse('reviews:product_reviews', kwargs={'product_id': self.object.product.id})


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vue pour modifier un avis existant.
    """
    model = Review
    form_class = ReviewEditForm
    template_name = 'reviews/review_form.html'
    pk_url_kwarg = 'review_id'
    
    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user or self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, _("Vous n'êtes pas autorisé à modifier cet avis."))
        return redirect('catalog:product_detail', pk=self.get_object().product.id)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Votre avis a été mis à jour avec succès !'))
        return response
    
    def get_success_url(self):
        return reverse('reviews:product_reviews', kwargs={'product_id': self.object.product.id})


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vue pour supprimer un avis.
    """
    model = Review
    pk_url_kwarg = 'review_id'
    template_name = 'reviews/review_confirm_delete.html'
    
    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Votre avis a été supprimé avec succès.'))
        return response
    
    def get_success_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.object.product.id})


@require_http_methods(["POST"])
@login_required
def toggle_review_like(request, review_id):
    """
    Vue pour aimer/ne plus aimer un avis (AJAX).
    """
    review = get_object_or_404(Review, id=review_id, is_approved=True)
    
    if review.user == request.user:
        return JsonResponse({
            'success': False,
            'message': _("Vous ne pouvez pas aimer votre propre avis.")
        }, status=400)
    
    if review.likes.filter(id=request.user.id).exists():
        review.likes.remove(request.user)
        liked = False
    else:
        review.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': review.likes.count()
    })

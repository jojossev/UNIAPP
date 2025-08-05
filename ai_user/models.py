from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class TranslationHistory(models.Model):
    """Historique des traductions effectuées par les utilisateurs"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='translations'
    )
    source_language = models.CharField('Langue source', max_length=10)
    target_language = models.CharField('Langue cible', max_length=10)
    original_text = models.TextField('Texte original')
    translated_text = models.TextField('Texte traduit')
    
    # Pour lier à n'importe quel modèle
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField('Date de création', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historique de traduction'
        verbose_name_plural = 'Historiques de traduction'
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Traduction {self.source_language} → {self.target_language} par {self.user or 'Anonyme'}"

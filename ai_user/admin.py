from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import TranslationHistory


class TranslationHistoryInline(GenericTabularInline):
    model = TranslationHistory
    extra = 0
    readonly_fields = ('created_at', 'source_language', 'target_language', 'user')
    can_delete = False
    max_num = 0
    show_change_link = True


@admin.register(TranslationHistory)
class TranslationHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'source_language', 'target_language', 'created_at')
    list_filter = ('source_language', 'target_language', 'created_at')
    search_fields = ('user__username', 'original_text', 'translated_text')
    readonly_fields = ('created_at', 'source_language', 'target_language', 'user', 'original_text', 'translated_text')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations de traduction', {
            'fields': ('user', 'source_language', 'target_language')
        }),
        ('Contenu', {
            'fields': ('original_text', 'translated_text')
        }),
        ('Liaisons génériques', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

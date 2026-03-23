from django.contrib import admin
from .models import ChatSession, ChatMessage, ResumeAnalysis, CareerRoadmap


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'tokens_used', 'created_at']
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    inlines = [ChatMessageInline]
    list_display = ['user', 'title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['user__email', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_filename',
                    'overall_score', 'ats_score', 'is_processed', 'created_at']
    list_filter = ['is_processed']
    search_fields = ['user__email', 'original_filename']
    readonly_fields = ['created_at', 'overall_score', 'ats_score']


@admin.register(CareerRoadmap)
class CareerRoadmapAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_role', 'experience_years', 'created_at']
    search_fields = ['user__email', 'target_role']
    readonly_fields = ['created_at']

from rest_framework import serializers
from .models import ChatSession, ChatMessage, ResumeAnalysis, CareerRoadmap


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'tokens_used', 'created_at']
        read_only_fields = ['id', 'role', 'tokens_used', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'context', 'created_at', 'updated_at',
                  'is_active', 'messages', 'last_message', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last = obj.messages.last()
        return last.content[:100] if last else None

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatSessionListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at',
                  'updated_at', 'last_message', 'message_count']

    def get_last_message(self, obj):
        last = obj.messages.last()
        return last.content[:100] if last else None

    def get_message_count(self, obj):
        return obj.messages.count()


class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000)
    session_id = serializers.IntegerField(required=False, allow_null=True)


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = [
            'id', 'original_filename', 'job_description', 'overall_score',
            'ats_score', 'summary', 'strengths', 'weaknesses', 'suggestions',
            'keywords_found', 'keywords_missing', 'created_at', 'is_processed',
        ]
        read_only_fields = [
            'id', 'overall_score', 'ats_score', 'summary', 'strengths',
            'weaknesses', 'suggestions', 'keywords_found', 'keywords_missing',
            'created_at', 'is_processed',
        ]


class ResumeUploadSerializer(serializers.Serializer):
    resume_file = serializers.FileField()
    job_description = serializers.CharField(
        required=False, allow_blank=True, max_length=3000)

    def validate_resume_file(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError('Only PDF files are supported.')
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError('File size must be under 5MB.')
        return value


class CareerRoadmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerRoadmap
        fields = ['id', 'target_role', 'current_skills', 'experience_years',
                  'roadmap_data', 'created_at']
        read_only_fields = ['id', 'roadmap_data', 'created_at']


class CareerRoadmapRequestSerializer(serializers.Serializer):
    target_role = serializers.CharField(max_length=200)
    current_skills = serializers.ListField(
        child=serializers.CharField(), default=list)
    experience_years = serializers.IntegerField(
        min_value=0, max_value=50, default=0)


class QuizRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=200)
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'], default='medium')
    count = serializers.IntegerField(min_value=3, max_value=20, default=5)

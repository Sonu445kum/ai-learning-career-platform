from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ChatSession, ChatMessage, ResumeAnalysis, CareerRoadmap
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer, SendMessageSerializer,
    ResumeAnalysisSerializer, ResumeUploadSerializer,
    CareerRoadmapSerializer, CareerRoadmapRequestSerializer,
    QuizRequestSerializer,
)
from .services import (
    chat_with_ai, extract_text_from_pdf,
    analyze_resume, generate_career_roadmap, generate_quiz_questions,
)


class ChatSessionListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatSessionDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class SendMessageView(APIView):
    """Send a message to the AI chatbot and get a response."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Get or create session
        session_id = data.get('session_id')
        if session_id:
            session = get_object_or_404(
                ChatSession, pk=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=data['message'][:50],
            )

        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role=ChatMessage.USER,
            content=data['message'],
        )

        # Build conversation history for context
        history = [
            {"role": m.role, "content": m.content}
            for m in session.messages.all()
        ]

        # Get AI response
        try:
            ai_response = chat_with_ai(
                history, session_context=session.context)
            assistant_msg = ChatMessage.objects.create(
                session=session,
                role=ChatMessage.ASSISTANT,
                content=ai_response['content'],
                tokens_used=ai_response['tokens_used'],
            )
            # Auto-generate session title from first message
            if session.messages.count() <= 2:
                session.title = data['message'][:80]
                session.save(update_fields=['title', 'updated_at'])

            return Response({
                'session_id': session.id,
                'session_title': session.title,
                'user_message': {'id': user_msg.id, 'content': user_msg.content, 'role': 'user'},
                'ai_message': {
                    'id': assistant_msg.id,
                    'content': assistant_msg.content,
                    'role': 'assistant',
                    'tokens_used': assistant_msg.tokens_used,
                },
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResumeAnalyzeView(APIView):
    """Upload PDF resume and get AI-powered feedback."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        resume_file = data['resume_file']
        job_description = data.get('job_description', '')

        # Extract text from PDF
        try:
            resume_text = extract_text_from_pdf(resume_file)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if len(resume_text) < 100:
            return Response({'error': 'Could not extract enough text from the resume.'}, status=400)

        # Save file reference
        resume_file.seek(0)
        analysis_obj = ResumeAnalysis.objects.create(
            user=request.user,
            resume_file=resume_file,
            original_filename=resume_file.name,
            job_description=job_description,
        )

        # Run AI analysis
        try:
            result = analyze_resume(resume_text, job_description)
            analysis_obj.overall_score = result.get('overall_score', 0)
            analysis_obj.ats_score = result.get('ats_score', 0)
            analysis_obj.summary = result.get('summary', '')
            analysis_obj.strengths = result.get('strengths', [])
            analysis_obj.weaknesses = result.get('weaknesses', [])
            analysis_obj.suggestions = result.get('suggestions', [])
            analysis_obj.keywords_found = result.get('keywords_found', [])
            analysis_obj.keywords_missing = result.get('keywords_missing', [])
            analysis_obj.is_processed = True
            analysis_obj.save()
        except Exception as e:
            analysis_obj.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(ResumeAnalysisSerializer(analysis_obj).data, status=status.HTTP_201_CREATED)


class ResumeAnalysisHistoryView(generics.ListAPIView):
    serializer_class = ResumeAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ResumeAnalysis.objects.filter(user=self.request.user, is_processed=True)


class CareerRoadmapView(APIView):
    """Generate an AI career roadmap."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CareerRoadmapRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            roadmap_data = generate_career_roadmap(
                target_role=data['target_role'],
                current_skills=data['current_skills'],
                experience_years=data['experience_years'],
            )
            roadmap = CareerRoadmap.objects.create(
                user=request.user,
                target_role=data['target_role'],
                current_skills=data['current_skills'],
                experience_years=data['experience_years'],
                roadmap_data=roadmap_data,
            )
            return Response(CareerRoadmapSerializer(roadmap).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        roadmaps = CareerRoadmap.objects.filter(user=request.user)
        return Response(CareerRoadmapSerializer(roadmaps, many=True).data)


class GenerateQuizView(APIView):
    """Generate AI quiz questions for a topic."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QuizRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            questions = generate_quiz_questions(
                topic=data['topic'],
                difficulty=data['difficulty'],
                count=data['count'],
            )
            return Response({'topic': data['topic'], 'questions': questions})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

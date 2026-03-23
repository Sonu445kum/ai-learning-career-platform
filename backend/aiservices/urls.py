from django.urls import path
from .views import (
    ChatSessionListView, ChatSessionDetailView, SendMessageView,
    ResumeAnalyzeView, ResumeAnalysisHistoryView,
    CareerRoadmapView,
    GenerateQuizView,
)

urlpatterns = [
    # Chat
    path('chat/sessions/', ChatSessionListView.as_view(), name='chat-sessions'),
    path('chat/sessions/<int:pk>/', ChatSessionDetailView.as_view(),
         name='chat-session-detail'),
    path('chat/send/', SendMessageView.as_view(), name='chat-send'),

    # Resume
    path('resume/analyze/', ResumeAnalyzeView.as_view(), name='resume-analyze'),
    path('resume/history/', ResumeAnalysisHistoryView.as_view(),
         name='resume-history'),

    # Career Roadmap
    path('career/roadmap/', CareerRoadmapView.as_view(), name='career-roadmap'),

    # Quiz Generator
    path('quiz/generate/', GenerateQuizView.as_view(), name='quiz-generate'),
]

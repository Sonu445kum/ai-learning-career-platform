from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message, Notification
from .serializers import (
    ChatRoomSerializer, MessageSerializer,
    NotificationSerializer,
)


class ChatRoomListView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user, is_active=True)

    def perform_create(self, serializer):
        room = serializer.save(created_by=self.request.user)
        room.members.add(self.request.user)


class ChatRoomDetailView(generics.RetrieveAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user, is_active=True)


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room = get_object_or_404(
            ChatRoom, slug=self.kwargs['room_slug'], members=self.request.user)
        return Message.objects.filter(room=room, is_deleted=False).select_related('sender')[:100]


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        if pk:
            notifications = Notification.objects.filter(
                pk=pk, user=request.user)
        else:
            notifications = Notification.objects.filter(
                user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({'message': 'Notifications marked as read.'})


class DashboardStatsView(APIView):
    """Dashboard stats for students and instructors."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        from courses.models import Enrollment, Course
        from ai_services.models import ChatSession, ResumeAnalysis

        if user.role == 'instructor':
            courses = Course.objects.filter(instructor=user)
            return Response({
                'total_courses': courses.count(),
                'published_courses': courses.filter(status='published').count(),
                'total_students': sum(c.total_students for c in courses),
                'total_revenue': sum(
                    p.amount for c in courses
                    for p in c.payments.filter(status='completed')
                ),
                'avg_rating': sum(c.average_rating for c in courses) / courses.count() if courses else 0,
            })
        else:
            enrollments = Enrollment.objects.filter(student=user)
            return Response({
                'enrolled_courses': enrollments.count(),
                'completed_courses': enrollments.filter(is_completed=True).count(),
                'in_progress_courses': enrollments.filter(is_completed=False).count(),
                'avg_progress': sum(e.progress_percent for e in enrollments) / enrollments.count() if enrollments else 0,
                'resume_analyses': ResumeAnalysis.objects.filter(user=user, is_processed=True).count(),
                'ai_sessions': ChatSession.objects.filter(user=user).count(),
                'unread_notifications': Notification.objects.filter(user=user, is_read=False).count(),
            })

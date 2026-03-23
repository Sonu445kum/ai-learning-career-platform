from django.urls import path
from .views import (
    ChatRoomListView, ChatRoomDetailView, MessageListView,
    NotificationListView, MarkNotificationReadView,
    DashboardStatsView,
)

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('chat/rooms/', ChatRoomListView.as_view(), name='chat-rooms'),
    path('chat/rooms/<slug:slug>/',
         ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('chat/rooms/<slug:room_slug>/messages/',
         MessageListView.as_view(), name='room-messages'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/',
         MarkNotificationReadView.as_view(), name='mark-all-read'),
    path('notifications/<int:pk>/read/',
         MarkNotificationReadView.as_view(), name='mark-read'),
]

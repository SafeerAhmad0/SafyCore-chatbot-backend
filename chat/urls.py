"""
URL configuration for chat app
"""
from django.urls import path
from .views import (
    ChatView,
    ChatStreamView,
    ConversationHistoryView,
    ClearConversationView,
    UserSessionsView
)

app_name = 'chat'

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
    path('stream/', ChatStreamView.as_view(), name='chat_stream'),
    path('sessions/', UserSessionsView.as_view(), name='user_sessions'),
    path('conversation/<str:session_id>/', ConversationHistoryView.as_view(), name='conversation_history'),
    path('conversation/<str:session_id>/clear/', ClearConversationView.as_view(), name='clear_conversation'),
]

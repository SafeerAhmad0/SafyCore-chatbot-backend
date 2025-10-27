"""
Chat models - stored in Supabase with Row Level Security (RLS)
This file defines the structure of data stored in Supabase tables
"""
from django.db import models
from users.models import UserProfile


class ConversationSession(models.Model):
    """
    Represents a conversation session (stored in Django for reference)
    Actual messages are stored in Supabase with RLS
    """
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversation_sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.session_id} - {self.user.email}"


# Note: Message data is stored in Supabase tables, not Django DB
# Supabase table structure:
#
# CREATE TABLE messages (
#   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#   user_id UUID NOT NULL REFERENCES auth.users(id),
#   session_id VARCHAR(255) NOT NULL,
#   role VARCHAR(50) NOT NULL CHECK (role IN ('system', 'user', 'assistant')),
#   content TEXT NOT NULL,
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# CREATE INDEX idx_messages_user_session ON messages(user_id, session_id);
#
# -- Row Level Security Policy
# ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
#
# CREATE POLICY "Users can only access their own messages"
#   ON messages
#   FOR ALL
#   USING (auth.uid() = user_id);
#
# CREATE TABLE training_data (
#   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#   user_id UUID NOT NULL REFERENCES auth.users(id),
#   session_id VARCHAR(255) NOT NULL,
#   content TEXT NOT NULL,
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
#   updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# CREATE INDEX idx_training_data_user_session ON training_data(user_id, session_id);
#
# ALTER TABLE training_data ENABLE ROW LEVEL SECURITY;
#
# CREATE POLICY "Users can only access their own training data"
#   ON training_data
#   FOR ALL
#   USING (auth.uid() = user_id);

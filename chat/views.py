"""
Chat views with Groq AI integration and Supabase storage
Each user's conversations are isolated using RLS in Supabase
"""
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from django.conf import settings
from groq import Groq
from safycore_backend.supabase_client import get_user_supabase_client
from .models import ConversationSession


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\|(.+?)\|', r'\1', text)
    return text.strip()


def get_system_prompt(training_data: str = None) -> str:
    """Generate system prompt with optional training data"""
    if training_data:
        return f"""You are a helpful assistant. Use the following information to answer questions:

{training_data}

Rules:
1. ONLY answer using the provided information
2. Use plain text, NO markdown formatting
3. Keep responses to 1-2 sentences maximum
4. Be conversational and helpful"""
    return "You are a helpful assistant. Provide concise, plain text responses without markdown formatting."


class ChatView(APIView):
    """
    Handle non-streaming chat messages
    Stores messages in Supabase with user isolation
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        session_id = request.data.get('session_id', 'default')
        training_data = request.data.get('training_data')

        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_profile = request.user
            supabase_user = request.supabase_user
            token = request.supabase_token

            # Get user-specific Supabase client with RLS
            supabase = get_user_supabase_client(token)

            # Get or create conversation session in Django
            conversation, created = ConversationSession.objects.get_or_create(
                session_id=session_id,
                user=user_profile,
                defaults={'title': message[:50]}
            )

            # Get conversation history from Supabase (RLS automatically filters by user)
            messages_response = supabase.table('messages').select('*').eq(
                'session_id', session_id
            ).order('created_at').execute()

            conversation_history = messages_response.data if messages_response.data else []

            # Check if this is first message - add training data
            if not conversation_history and training_data:
                system_message = {
                    'user_id': supabase_user.id,
                    'session_id': session_id,
                    'role': 'system',
                    'content': get_system_prompt(training_data)
                }
                supabase.table('messages').insert(system_message).execute()

                # Store training data in Supabase
                training_record = {
                    'user_id': supabase_user.id,
                    'session_id': session_id,
                    'content': training_data
                }
                supabase.table('training_data').insert(training_record).execute()

                conversation_history.append(system_message)
            elif not conversation_history:
                # Default system message
                system_message = {
                    'user_id': supabase_user.id,
                    'session_id': session_id,
                    'role': 'system',
                    'content': get_system_prompt()
                }
                supabase.table('messages').insert(system_message).execute()
                conversation_history.append(system_message)

            # Add user message
            user_message = {
                'user_id': supabase_user.id,
                'session_id': session_id,
                'role': 'user',
                'content': message
            }
            supabase.table('messages').insert(user_message).execute()
            conversation_history.append(user_message)

            # Prepare messages for Groq
            groq_messages = [
                {'role': msg['role'], 'content': msg['content']}
                for msg in conversation_history
            ]

            # Call Groq API
            groq_client = Groq(api_key=settings.GROQ_API_KEY)
            chat_completion = groq_client.chat.completions.create(
                messages=groq_messages,
                model="openai/gpt-oss-120b",
                temperature=0.3,
                max_completion_tokens=100,
                top_p=0.9,
                stream=False
            )

            assistant_response = chat_completion.choices[0].message.content
            clean_response = strip_markdown(assistant_response)

            # Store assistant message in Supabase
            assistant_message = {
                'user_id': supabase_user.id,
                'session_id': session_id,
                'role': 'assistant',
                'content': clean_response
            }
            supabase.table('messages').insert(assistant_message).execute()

            # Update conversation timestamp
            conversation.save()

            return Response({
                'response': clean_response,
                'session_id': session_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatStreamView(APIView):
    """
    Handle streaming chat messages
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        session_id = request.data.get('session_id', 'default')
        training_data = request.data.get('training_data')

        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_profile = request.user
            supabase_user = request.supabase_user
            token = request.supabase_token

            # Get user-specific Supabase client
            supabase = get_user_supabase_client(token)

            # Get or create conversation session
            conversation, created = ConversationSession.objects.get_or_create(
                session_id=session_id,
                user=user_profile,
                defaults={'title': message[:50]}
            )

            # Get conversation history
            messages_response = supabase.table('messages').select('*').eq(
                'session_id', session_id
            ).order('created_at').execute()

            conversation_history = messages_response.data if messages_response.data else []

            # Handle training data for first message
            if not conversation_history and training_data:
                system_message = {
                    'user_id': supabase_user.id,
                    'session_id': session_id,
                    'role': 'system',
                    'content': get_system_prompt(training_data)
                }
                supabase.table('messages').insert(system_message).execute()
                training_record = {
                    'user_id': supabase_user.id,
                    'session_id': session_id,
                    'content': training_data
                }
                supabase.table('training_data').insert(training_record).execute()
                conversation_history.append(system_message)
            elif not conversation_history:
                system_message = {
                    'user_id': supabase_user.id,
                    'session_id': session_id,
                    'role': 'system',
                    'content': get_system_prompt()
                }
                supabase.table('messages').insert(system_message).execute()
                conversation_history.append(system_message)

            # Add user message
            user_message = {
                'user_id': supabase_user.id,
                'session_id': session_id,
                'role': 'user',
                'content': message
            }
            supabase.table('messages').insert(user_message).execute()
            conversation_history.append(user_message)

            # Prepare messages for Groq
            groq_messages = [
                {'role': msg['role'], 'content': msg['content']}
                for msg in conversation_history
            ]

            # Streaming generator
            def generate():
                full_response = ""
                groq_client = Groq(api_key=settings.GROQ_API_KEY)

                stream = groq_client.chat.completions.create(
                    messages=groq_messages,
                    model="openai/gpt-oss-120b",
                    temperature=0.3,
                    max_completion_tokens=100,
                    top_p=0.9,
                    stream=True
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content

                # Clean and store full response
                clean_response = strip_markdown(full_response)
                assistant_message = {
                    'user_id': supabase_user.id,
                    'session_id': session_id,
                    'role': 'assistant',
                    'content': clean_response
                }
                supabase.table('messages').insert(assistant_message).execute()

                # Update conversation
                conversation.save()

            return StreamingHttpResponse(generate(), content_type='text/plain')

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationHistoryView(APIView):
    """
    Get conversation history for a session
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            token = request.supabase_token
            supabase = get_user_supabase_client(token)

            # Get messages (RLS automatically filters by user)
            messages_response = supabase.table('messages').select('*').eq(
                'session_id', session_id
            ).order('created_at').execute()

            messages = messages_response.data if messages_response.data else []

            return Response({
                'session_id': session_id,
                'messages': messages
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClearConversationView(APIView):
    """
    Clear conversation history for a session
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, session_id):
        try:
            user_profile = request.user
            token = request.supabase_token
            supabase = get_user_supabase_client(token)

            # Delete messages from Supabase (RLS ensures only user's messages are deleted)
            supabase.table('messages').delete().eq('session_id', session_id).execute()

            # Delete training data
            supabase.table('training_data').delete().eq('session_id', session_id).execute()

            # Delete Django session record
            ConversationSession.objects.filter(
                session_id=session_id,
                user=user_profile
            ).delete()

            return Response({
                'message': 'Conversation cleared successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSessionsView(APIView):
    """
    Get all conversation sessions for authenticated user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = request.user
            sessions = ConversationSession.objects.filter(user=user_profile)

            sessions_data = [{
                'session_id': session.session_id,
                'title': session.title,
                'created_at': session.created_at,
                'updated_at': session.updated_at
            } for session in sessions]

            return Response({
                'sessions': sessions_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

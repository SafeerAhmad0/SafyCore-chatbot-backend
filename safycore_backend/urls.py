"""
URL configuration for safycore_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'SafyCore Backend API',
        'version': '2.0',
        'endpoints': {
            'auth': {
                'signup': '/api/auth/signup/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'profile': '/api/auth/profile/',
                'password_reset': '/api/auth/password-reset/',
                'password_reset_confirm': '/api/auth/password-reset/confirm/',
                'change_password': '/api/auth/change-password/',
            },
            'chat': {
                'chat': '/api/chat/',
                'stream': '/api/chat/stream/',
                'sessions': '/api/chat/sessions/',
                'history': '/api/chat/conversation/<session_id>/',
                'clear': '/api/chat/conversation/<session_id>/clear/',
            }
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api_root'),
    path('api/auth/', include('users.urls')),
    path('api/chat/', include('chat.urls')),
]

"""
URL configuration for config project.

Todas las rutas de la API están bajo /api/
Se incluyen las rutas definidas en api/routes/urls.py
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API REST — todos los endpoints bajo /api/
    path('api/', include('api.routes.urls')),
    # Frontend — Login
    path('login', TemplateView.as_view(template_name='login.html'), name='login'),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login-html'),
    # Frontend — Dashboard (raíz)
    path('', TemplateView.as_view(template_name='index.html'), name='frontend'),
]

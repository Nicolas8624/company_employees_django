"""
URL configuration for config project.

Todas las rutas de la API están bajo /api/
Se incluyen las rutas definidas en api/routes/urls.py
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # API REST — todos los endpoints bajo /api/
    path('api/', include('api.routes.urls')),
]

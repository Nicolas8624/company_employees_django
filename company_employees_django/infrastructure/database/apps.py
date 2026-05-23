"""
Configuración de la app de base de datos.

Esta app contiene los modelos ORM de Django para
las entidades Compania y Empleado.
"""
from django.apps import AppConfig


class DatabaseConfig(AppConfig):
    """Configuración de la app infrastructure.database."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infrastructure.database'
    verbose_name = 'Base de Datos'
    label = 'database'

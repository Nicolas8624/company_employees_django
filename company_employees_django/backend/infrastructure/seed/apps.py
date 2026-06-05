"""
Configuración de la app de seed.

Esta app contiene los comandos de management para
poblar la base de datos con datos de prueba.
"""
from django.apps import AppConfig


class SeedConfig(AppConfig):
    """Configuración de la app infrastructure.seed."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infrastructure.seed'
    verbose_name = 'Seed Data'
    label = 'seed'

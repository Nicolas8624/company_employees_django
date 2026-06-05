"""
Serializers para Compañía.

Manejan la validación de entrada y la serialización de salida
para los endpoints de compañías.
"""
from rest_framework import serializers


class CompaniaSerializer(serializers.Serializer):
    """Serializer para respuesta de compañía."""

    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(max_length=200)
    direccion = serializers.CharField(max_length=300)
    telefono = serializers.CharField(max_length=50)
    fecha_creacion = serializers.DateTimeField(read_only=True)


class CompaniaCreateSerializer(serializers.Serializer):
    """Serializer para creación de compañía."""

    nombre = serializers.CharField(max_length=200, required=True)
    direccion = serializers.CharField(max_length=300, required=True)
    telefono = serializers.CharField(max_length=50, required=True)


class CompaniaPatchSerializer(serializers.Serializer):
    """Serializer para actualización parcial de compañía."""

    nombre = serializers.CharField(max_length=200, required=False)
    direccion = serializers.CharField(max_length=300, required=False)
    telefono = serializers.CharField(max_length=50, required=False)

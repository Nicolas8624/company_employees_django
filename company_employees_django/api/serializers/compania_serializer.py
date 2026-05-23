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
    """Serializer para creación/actualización de compañía."""

    nombre = serializers.CharField(max_length=200, required=True)
    direccion = serializers.CharField(max_length=300, required=True)
    telefono = serializers.CharField(max_length=50, required=True)

    def validate_nombre(self, value: str) -> str:
        """Validar que el nombre no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value.strip()

    def validate_telefono(self, value: str) -> str:
        """Validar formato básico de teléfono."""
        if not value.strip():
            raise serializers.ValidationError("El teléfono no puede estar vacío.")
        return value.strip()

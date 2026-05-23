"""
Serializers para Empleado.

Manejan la validación de entrada y la serialización de salida
para los endpoints de empleados.
"""
from rest_framework import serializers


class EmpleadoSerializer(serializers.Serializer):
    """Serializer para respuesta de empleado."""

    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    correo = serializers.EmailField(max_length=200)
    cargo = serializers.CharField(max_length=150)
    salario = serializers.DecimalField(max_digits=12, decimal_places=2)
    compania_id = serializers.IntegerField()


class EmpleadoCreateSerializer(serializers.Serializer):
    """Serializer para creación/actualización de empleado."""

    nombre = serializers.CharField(max_length=100, required=True)
    apellido = serializers.CharField(max_length=100, required=True)
    correo = serializers.EmailField(max_length=200, required=True)
    cargo = serializers.CharField(max_length=150, required=True)
    salario = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=True
    )
    compania_id = serializers.IntegerField(required=True)

    def validate_salario(self, value):
        """Validar que el salario sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El salario debe ser mayor a cero.")
        return value

    def validate_correo(self, value: str) -> str:
        """Validar formato de correo."""
        if not value.strip():
            raise serializers.ValidationError("El correo no puede estar vacío.")
        return value.strip().lower()

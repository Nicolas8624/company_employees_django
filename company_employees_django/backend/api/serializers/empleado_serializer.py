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
    """Serializer para creación de empleado."""

    nombre = serializers.CharField(max_length=100, required=True)
    apellido = serializers.CharField(max_length=100, required=True)
    correo = serializers.EmailField(max_length=200, required=True)
    cargo = serializers.CharField(max_length=150, required=True)
    salario = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=True
    )
    compania_id = serializers.IntegerField(required=True)


class EmpleadoPatchSerializer(serializers.Serializer):
    """Serializer para actualización parcial de empleado."""

    nombre = serializers.CharField(max_length=100, required=False)
    apellido = serializers.CharField(max_length=100, required=False)
    correo = serializers.EmailField(max_length=200, required=False)
    cargo = serializers.CharField(max_length=150, required=False)
    salario = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    compania_id = serializers.IntegerField(required=False)


class EmpleadoBulkCreateSerializer(serializers.Serializer):
    """Serializer para creación masiva."""
    empleados = EmpleadoCreateSerializer(many=True)


class BulkDeleteSerializer(serializers.Serializer):
    """Serializer para eliminación masiva."""
    ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

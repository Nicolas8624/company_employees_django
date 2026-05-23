"""
Serializer para el endpoint transaccional: Compañía con Empleados.

Valida la estructura de datos para crear una compañía
junto con múltiples empleados en una sola transacción.
"""
from rest_framework import serializers


class EmpleadoEnCompaniaSerializer(serializers.Serializer):
    """Serializer para un empleado dentro del payload transaccional."""

    nombre = serializers.CharField(max_length=100, required=True)
    apellido = serializers.CharField(max_length=100, required=True)
    correo = serializers.EmailField(max_length=200, required=True)
    cargo = serializers.CharField(max_length=150, required=True)
    salario = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=True
    )

    def validate_salario(self, value):
        """Validar que el salario sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El salario debe ser mayor a cero.")
        return value


class CompaniaConEmpleadosSerializer(serializers.Serializer):
    """
    Serializer para POST /api/companias/con-empleados.

    Valida:
    - datos de la compañía (nombre, dirección, teléfono)
    - lista de empleados (al menos uno)
    """

    nombre = serializers.CharField(max_length=200, required=True)
    direccion = serializers.CharField(max_length=300, required=True)
    telefono = serializers.CharField(max_length=50, required=True)
    empleados = EmpleadoEnCompaniaSerializer(many=True, required=True)

    def validate_empleados(self, value):
        """Validar que haya al menos un empleado."""
        if not value:
            raise serializers.ValidationError(
                "Debe incluir al menos un empleado."
            )
        return value

    def validate_nombre(self, value: str) -> str:
        """Validar que el nombre no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value.strip()

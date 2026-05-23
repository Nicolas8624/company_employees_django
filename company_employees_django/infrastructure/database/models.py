"""
Modelos de Django ORM para la base de datos.

Estos modelos representan las tablas de la base de datos.
Solo la capa de Infrastructure los usa directamente.
"""
from django.db import models


class CompaniaModel(models.Model):
    """Modelo ORM para la tabla de compañías."""

    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    direccion = models.CharField(max_length=300, verbose_name="Dirección")
    telefono = models.CharField(max_length=50, verbose_name="Teléfono")
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )

    class Meta:
        db_table = "companias"
        verbose_name = "Compañía"
        verbose_name_plural = "Compañías"
        ordering = ["-fecha_creacion"]

    def __str__(self) -> str:
        return self.nombre


class EmpleadoModel(models.Model):
    """Modelo ORM para la tabla de empleados."""

    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    correo = models.EmailField(max_length=200, verbose_name="Correo electrónico")
    cargo = models.CharField(max_length=150, verbose_name="Cargo")
    salario = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Salario"
    )
    compania = models.ForeignKey(
        CompaniaModel,
        on_delete=models.CASCADE,
        related_name="empleados",
        verbose_name="Compañía",
    )

    class Meta:
        db_table = "empleados"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["apellido", "nombre"]

    def __str__(self) -> str:
        return f"{self.nombre} {self.apellido}"

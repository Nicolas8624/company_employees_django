"""
Pruebas unitarias y de integración para la API REST.

Verifican el comportamiento del UnitOfWork, los repositorios,
los servicios y la funcionalidad transaccional (rollback).
"""
from decimal import Decimal
from django.test import TestCase

from application.services.compania_service import CompaniaService
from application.services.empleado_service import EmpleadoService
from infrastructure.database.models import CompaniaModel, EmpleadoModel
from infrastructure.unit_of_work.unit_of_work import UnitOfWork


class OnionArchitectureTestCase(TestCase):
    """Pruebas para comprobar el flujo de Onion Architecture y transacciones."""

    def setUp(self) -> None:
        """Preparación antes de cada caso de prueba."""
        self.uow = UnitOfWork()
        self.compania_service = CompaniaService(self.uow)
        self.empleado_service = EmpleadoService(self.uow)

    def test_crear_compania_flujo_completo(self):
        """Probar creación de compañía y recuperación mediante servicios."""
        compania_data = {
            "nombre": "Prueba Unit Corp",
            "direccion": "Calle de las Pruebas 123",
            "telefono": "+57 601 999-9999",
        }
        
        # Crear usando el servicio
        compania_creada = self.compania_service.create_compania(compania_data)
        self.assertIsNotNone(compania_creada.id)
        self.assertEqual(compania_creada.nombre, "Prueba Unit Corp")

        # Verificar en base de datos ORM
        exists = CompaniaModel.objects.filter(pk=compania_creada.id).exists()
        self.assertTrue(exists)

    def test_crear_empleado_flujo_completo(self):
        """Probar creación de empleado asociado a compañía."""
        # 1. Crear compañía
        compania = self.compania_service.create_compania({
            "nombre": "Compania Empleados Test",
            "direccion": "Direccion Test",
            "telefono": "12345"
        })
        
        # 2. Crear empleado
        empleado_data = {
            "nombre": "Juanita",
            "apellido": "Perez",
            "correo": "juanita@perez.com",
            "cargo": "QA Automation",
            "salario": Decimal("5000000.00"),
            "compania_id": compania.id
        }
        
        empleado_creado = self.empleado_service.create_empleado(empleado_data)
        self.assertIsNotNone(empleado_creado.id)
        self.assertEqual(empleado_creado.nombre, "Juanita")
        self.assertEqual(empleado_creado.compania_id, compania.id)

    def test_endpoint_transaccional_exito(self):
        """Probar transacción exitosa (crear compañía y múltiples empleados)."""
        payload = {
            "nombre": "Transac Corp S.A.",
            "direccion": "Zona Franca",
            "telefono": "555-5555",
            "empleados": [
                {
                    "nombre": "Empleado 1",
                    "apellido": "Test",
                    "correo": "emp1@test.com",
                    "cargo": "Dev",
                    "salario": Decimal("3000000.00")
                },
                {
                    "nombre": "Empleado 2",
                    "apellido": "Test",
                    "correo": "emp2@test.com",
                    "cargo": "Dev Lead",
                    "salario": Decimal("6000000.00")
                }
            ]
        }

        resultado = self.compania_service.create_compania_con_empleados(payload)
        
        # Verificar compañía
        compania_id = resultado["compania"].id
        self.assertIsNotNone(compania_id)
        self.assertTrue(CompaniaModel.objects.filter(pk=compania_id).exists())

        # Verificar empleados
        empleados = resultado["empleados"]
        self.assertEqual(len(empleados), 2)
        for emp in empleados:
            self.assertIsNotNone(emp.id)
            self.assertEqual(emp.compania_id, compania_id)
            self.assertTrue(EmpleadoModel.objects.filter(pk=emp.id).exists())

    def test_endpoint_transaccional_rollback(self):
        """Probar que un fallo provoca rollback completo (nada se guarda)."""
        # Datos iniciales en la base de datos
        companias_antes = CompaniaModel.objects.count()
        empleados_antes = EmpleadoModel.objects.count()

        payload = {
            "nombre": "Compañia Rollback Corp",
            "direccion": "Calle Invalida",
            "telefono": "000-0000",
            "empleados": [
                {
                    "nombre": "Empleado Valido",
                    "apellido": "Test",
                    "correo": "valido@test.com",
                    "cargo": "Dev",
                    "salario": Decimal("4000000.00")
                },
                {
                    "nombre": "Empleado Invalido",
                    "apellido": "Test",
                    "correo": "correo-erroneo",
                    "cargo": "Hacker",
                    # Causamos un error de persistencia lanzando una excepción
                    # al mapear o forzando un error de tipo en el salario
                    "salario": None 
                }
            ]
        }

        # Intentar ejecutar transacción - debe lanzar excepción
        with self.assertRaises(Exception):
            self.compania_service.create_compania_con_empleados(payload)

        # Verificar que NO se insertó nada
        self.assertEqual(CompaniaModel.objects.count(), companias_antes)
        self.assertEqual(EmpleadoModel.objects.count(), empleados_antes)

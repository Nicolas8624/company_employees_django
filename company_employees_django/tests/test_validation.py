"""
Pruebas para las validaciones del Módulo 3.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth.hashers import make_password
from infrastructure.database.models import CompaniaModel, EmpleadoModel, UsuarioModel


class ValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario ADMIN y autenticar
        self.admin = UsuarioModel.objects.create(
            correo="admin@test.com",
            password_hash=make_password("Pass123!"),
            rol="ADMIN"
        )
        resp = self.client.post("/api/auth/login", {"correo": "admin@test.com", "password": "Pass123!"}, format="json")
        token = resp.data.get("token")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.compania = CompaniaModel.objects.create(
            nombre="Compania Validacion",
            direccion="Dir 123",
            telefono="555-0000"
        )
        self.emp_base = EmpleadoModel.objects.create(
            nombre="Test",
            apellido="Validacion",
            correo="unico@test.com",
            cargo="Dev",
            salario=1000,
            compania_id=self.compania.pk
        )

    def test_crear_empleado_correo_duplicado(self):
        url = "/api/empleados"
        data = {
            "nombre": "Otro",
            "apellido": "Mas",
            "correo": "unico@test.com", # Duplicado
            "cargo": "QA",
            "salario": 1200,
            "compania_id": self.compania.pk
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errores", response.data)
        
        # Debe decir que el correo ya está registrado
        errores = response.data["errores"]
        self.assertTrue(any(e["campo"] == "correo" for e in errores))

    def test_crear_empleado_compania_inexistente(self):
        url = "/api/empleados"
        data = {
            "nombre": "Falla",
            "apellido": "Cia",
            "correo": "nuevo@test.com",
            "cargo": "QA",
            "salario": 1200,
            "compania_id": 9999 # No existe
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        errores = response.data["errores"]
        self.assertTrue(any(e["campo"] == "compania_id" for e in errores))

    def test_crear_compania_con_empleados_rollback(self):
        """Prueba del rollback transaccional requerido en el módulo 4 y módulo 3."""
        url = "/api/companias/con-empleados"
        data = {
            "nombre": "Compania Rollback",
            "direccion": "Falsa 123",
            "telefono": "123",
            "empleados": [
                {
                    "nombre": "Bien",
                    "apellido": "Hecho",
                    "correo": "bien@test.com",
                    "cargo": "Dev",
                    "salario": 1000
                },
                {
                    "nombre": "Mal",
                    "apellido": "Hecho",
                    "correo": "unico@test.com", # Duplicado que causará error de validación
                    "cargo": "Dev",
                    "salario": 1000
                }
            ]
        }
        
        # El correo duplicado debería cancelar todo (compania y empleado válido)
        compania_count_before = CompaniaModel.objects.count()
        empleado_count_before = EmpleadoModel.objects.count()
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertEqual(CompaniaModel.objects.count(), compania_count_before)
        self.assertEqual(EmpleadoModel.objects.count(), empleado_count_before)

    def test_admin_medellin_has_full_crud(self):
        """Prueba de que un administrador de Medellín posee acceso completo (POST)."""
        admin_med = UsuarioModel.objects.create(
            correo="admin_med@test.com",
            password_hash=make_password("Pass123!"),
            rol="ADMIN",
            ciudad="Medellín"
        )
        # Iniciar sesión
        resp = self.client.post("/api/auth/login", {"correo": "admin_med@test.com", "password": "Pass123!"}, format="json")
        token = resp.data.get("token")
        
        client_med = APIClient()
        client_med.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        # Intentar POST de Compañía
        url = "/api/companias"
        data = {
            "nombre": "TechCorp Medellín",
            "direccion": "Calle 10",
            "telefono": "12345"
        }
        response = client_med.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_bogota_restricted_delete_only(self):
        """Un administrador de Bogotá puede crear y actualizar, pero no eliminar."""
        UsuarioModel.objects.create(
            correo="admin_bog@test.com",
            password_hash=make_password("Pass123!"),
            rol="ADMIN",
            ciudad="Bogotá",
        )
        resp = self.client.post(
            "/api/auth/login",
            {"correo": "admin_bog@test.com", "password": "Pass123!"},
            format="json",
        )
        token = resp.data.get("token")

        client_bog = APIClient()
        client_bog.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = "/api/companias"
        data = {
            "nombre": "TechCorp Bogotá",
            "direccion": "Calle 80",
            "telefono": "54321",
        }
        response = client_bog.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url_detail = f"/api/companias/{self.compania.pk}"
        response_put = client_bog.put(url_detail, data, format="json")
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)

        data_patch = {"telefono": "999-9999"}
        response_patch = client_bog.patch(url_detail, data_patch, format="json")
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(response_patch.data["telefono"], "999-9999")

        response_delete = client_bog.delete(url_detail)
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "los administradores de Bogotá no pueden eliminar",
            response_delete.data["detail"],
        )

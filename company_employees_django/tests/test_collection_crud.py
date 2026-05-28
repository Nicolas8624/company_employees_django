"""
Pruebas para las operaciones CRUD de colecciones (Módulo 1).
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth.hashers import make_password
from infrastructure.database.models import CompaniaModel, EmpleadoModel, UsuarioModel

class CollectionCrudTests(TestCase):
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

        # Crear compañía base
        self.compania = CompaniaModel.objects.create(
            nombre="Compania Base",
            direccion="Dir 123",
            telefono="555-0000"
        )
        # Crear empleados base
        self.emp1 = EmpleadoModel.objects.create(
            nombre="Juan",
            apellido="Perez",
            correo="juan@test.com",
            cargo="Dev",
            salario=1000,
            compania_id=self.compania.pk
        )
        self.emp2 = EmpleadoModel.objects.create(
            nombre="Maria",
            apellido="Gomez",
            correo="maria@test.com",
            cargo="QA",
            salario=1200,
            compania_id=self.compania.pk
        )

    def test_bulk_create_empleados(self):
        url = "/api/empleados/bulk"
        data = {
            "empleados": [
                {
                    "nombre": "Ana",
                    "apellido": "Lopez",
                    "correo": "ana@test.com",
                    "cargo": "PO",
                    "salario": 2000,
                    "compania_id": self.compania.pk
                },
                {
                    "nombre": "Luis",
                    "apellido": "Martinez",
                    "correo": "luis@test.com",
                    "cargo": "DevOps",
                    "salario": 2500,
                    "compania_id": self.compania.pk
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(EmpleadoModel.objects.count(), 4)

    def test_patch_empleado(self):
        url = f"/api/empleados/{self.emp1.pk}"
        data = {
            "salario": 1500,
            "cargo": "Senior Dev"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.emp1.refresh_from_db()
        self.assertEqual(self.emp1.salario, 1500)
        self.assertEqual(self.emp1.cargo, "Senior Dev")
        self.assertEqual(self.emp1.nombre, "Juan") # Unchanged

    def test_bulk_delete_empleados(self):
        url = "/api/empleados/bulk-delete"
        data = {
            "ids": [self.emp1.pk, self.emp2.pk]
        }
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["eliminados"], 2)
        self.assertEqual(EmpleadoModel.objects.count(), 0)

    def test_paginated_empleados(self):
        url = "/api/empleados?pagina=1&tamano=1&orden=nombre&dir=asc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("datos", response.data)
        self.assertIn("total", response.data)
        self.assertEqual(response.data["tamano"], 1)
        self.assertEqual(len(response.data["datos"]), 1)
        # Should be Juan because "Juan" vs "Maria", Juan is first ascending
        self.assertEqual(response.data["datos"][0]["nombre"], "Juan")

    def test_search_paginated_empleados(self):
        url = "/api/empleados?pagina=1&tamano=10&buscar=Maria"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["datos"][0]["nombre"], "Maria")

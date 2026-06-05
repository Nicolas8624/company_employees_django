"""
Pruebas unitarias para CompaniaRepository y EmpleadoRepository.

Comprueban directamente la interacción con Django ORM sin pasar por los servicios ni controladores.
"""
from decimal import Decimal
from django.test import TestCase
from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from infrastructure.database.models import CompaniaModel, EmpleadoModel
from infrastructure.repositories.compania_repository import CompaniaRepository
from infrastructure.repositories.empleado_repository import EmpleadoRepository


class RepositoryTests(TestCase):
    """Pruebas directas de los repositorios de infraestructura."""

    def setUp(self):
        self.compania_repo = CompaniaRepository()
        self.empleado_repo = EmpleadoRepository()

    def test_compania_repository_crud(self):
        # 1. Crear compañía
        compania_entity = Compania(
            nombre="Repo Corp",
            direccion="Calle Falsa 123",
            telefono="555-1234"
        )
        created = self.compania_repo.create(compania_entity)
        self.assertIsNotNone(created.id)
        self.assertEqual(created.nombre, "Repo Corp")

        # Verificar que existe en la DB
        self.assertTrue(CompaniaModel.objects.filter(pk=created.id).exists())

        # 2. Obtener por ID
        retrieved = self.compania_repo.get_by_id(created.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.nombre, "Repo Corp")

        # 3. Obtener inexistente
        self.assertIsNone(self.compania_repo.get_by_id(99999))

        # 4. Obtener todas
        all_cia = self.compania_repo.get_all()
        self.assertEqual(len(all_cia), 1)

        # 5. Condición de búsqueda
        found = self.compania_repo.find_by_condition(nombre="Repo Corp")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, created.id)

        # 6. Actualizar (PUT)
        updated = self.compania_repo.update(created.id, {
            "nombre": "Repo Corp Actualizada",
            "direccion": "Nueva Calle"
        })
        self.assertIsNotNone(updated)
        self.assertEqual(updated.nombre, "Repo Corp Actualizada")
        self.assertEqual(updated.direccion, "Nueva Calle")

        # 7. Actualización parcial (PATCH)
        patched = self.compania_repo.patch(created.id, {"telefono": "999-9999"})
        self.assertIsNotNone(patched)
        self.assertEqual(patched.telefono, "999-9999")

        # 8. Eliminar
        deleted = self.compania_repo.delete(created.id)
        self.assertTrue(deleted)
        self.assertFalse(CompaniaModel.objects.filter(pk=created.id).exists())
        self.assertFalse(self.compania_repo.delete(created.id))

    def test_empleado_repository_operations(self):
        # Crear compañía de prueba en DB
        cia_model = CompaniaModel.objects.create(
            nombre="Compania Empleados",
            direccion="Direccion",
            telefono="123"
        )

        # 1. Crear empleado
        empleado_entity = Empleado(
            nombre="Pepito",
            apellido="Perez",
            correo="pepito@perez.com",
            cargo="Junior Dev",
            salario=Decimal("1500.00"),
            compania_id=cia_model.pk
        )
        created = self.empleado_repo.create(empleado_entity)
        self.assertIsNotNone(created.id)
        self.assertEqual(created.nombre, "Pepito")
        self.assertEqual(created.compania_id, cia_model.pk)

        # Verificar en DB
        self.assertTrue(EmpleadoModel.objects.filter(pk=created.id).exists())

        # 2. Buscar por id y obtener por compañía
        retrieved = self.empleado_repo.get_by_id(created.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.nombre, "Pepito")

        emps_cia = self.empleado_repo.get_by_compania(cia_model.pk)
        self.assertEqual(len(emps_cia), 1)
        self.assertEqual(emps_cia[0].id, created.id)

        # 3. Actualizar (PUT) y PATCH
        updated = self.empleado_repo.update(created.id, {
            "nombre": "Pepito Update",
            "salario": Decimal("2000.00")
        })
        self.assertIsNotNone(updated)
        self.assertEqual(updated.nombre, "Pepito Update")
        self.assertEqual(updated.salario, Decimal("2000.00"))

        patched = self.empleado_repo.patch(created.id, {"cargo": "Senior Dev"})
        self.assertIsNotNone(patched)
        self.assertEqual(patched.cargo, "Senior Dev")

        # 4. Eliminar
        deleted = self.empleado_repo.delete(created.id)
        self.assertTrue(deleted)
        self.assertFalse(EmpleadoModel.objects.filter(pk=created.id).exists())

    def test_bulk_create_and_delete_many(self):
        cia = CompaniaModel.objects.create(nombre="Bulk Cia", direccion="X", telefono="0")
        
        # 1. Bulk Create
        empleados = [
            Empleado(nombre="E1", apellido="L1", correo="e1@bulk.com", cargo="D", salario=Decimal("1"), compania_id=cia.pk),
            Empleado(nombre="E2", apellido="L2", correo="e2@bulk.com", cargo="D", salario=Decimal("2"), compania_id=cia.pk),
            Empleado(nombre="E3", apellido="L3", correo="e3@bulk.com", cargo="D", salario=Decimal("3"), compania_id=cia.pk)
        ]
        
        created_list = self.empleado_repo.bulk_create(empleados)
        self.assertEqual(len(created_list), 3)
        
        ids = []
        for emp in created_list:
            self.assertIsNotNone(emp.id)
            ids.append(emp.id)
            
        # Verificar count en base de datos
        self.assertEqual(EmpleadoModel.objects.filter(compania_id=cia.pk).count(), 3)
        
        # 2. Delete Many
        deleted_count = self.empleado_repo.delete_many(ids)
        self.assertEqual(deleted_count, 3)
        self.assertEqual(EmpleadoModel.objects.filter(compania_id=cia.pk).count(), 0)

    def test_repository_pagination_and_sorting(self):
        # Crear datos de prueba
        for i in range(15):
            CompaniaModel.objects.create(
                nombre=f"Cia Paginada {i:02d}",
                direccion=f"Calle {15-i}",
                telefono=str(i)
            )

        # 1. Probar paginación simple (página 1, tamaño 5)
        res = self.compania_repo.get_paginated(page=1, size=5, sort_by="nombre", sort_dir="asc", search="")
        self.assertEqual(res["total"], 15)
        self.assertEqual(res["total_paginas"], 3)
        self.assertEqual(res["pagina"], 1)
        self.assertEqual(res["tamano"], 5)
        self.assertEqual(len(res["datos"]), 5)
        # Primer elemento debe ser Cia Paginada 00 por orden ascendente
        self.assertEqual(res["datos"][0].nombre, "Cia Paginada 00")

        # 2. Probar orden descendente
        res_desc = self.compania_repo.get_paginated(page=1, size=5, sort_by="nombre", sort_dir="desc", search="")
        self.assertEqual(res_desc["datos"][0].nombre, "Cia Paginada 14")

        # 3. Probar búsqueda
        res_search = self.compania_repo.get_paginated(page=1, size=5, sort_by="nombre", sort_dir="asc", search="05")
        self.assertEqual(res_search["total"], 1)
        self.assertEqual(res_search["datos"][0].nombre, "Cia Paginada 05")

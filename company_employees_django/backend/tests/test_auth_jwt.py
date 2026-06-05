"""
Pruebas de Módulo 4 — Seguridad JWT y Roles.
Pruebas de Módulo 5 — Política EsPropietarioDeCompania.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.hashers import make_password

from infrastructure.database.models import CompaniaModel, EmpleadoModel, UsuarioModel


def _get_token(client, correo, password):
    """Helper: obtener token JWT via login."""
    resp = client.post("/api/auth/login", {"correo": correo, "password": password}, format="json")
    return resp.data.get("token")


class AuthRegistroLoginTests(TestCase):
    """Módulo 4 — Registro y Login."""

    def setUp(self):
        self.client = APIClient()
        self.compania = CompaniaModel.objects.create(
            nombre="Cia JWT", direccion="Dir", telefono="000"
        )

    def test_registro_exitoso(self):
        data = {
            "correo": "nuevo@test.com",
            "password": "Pass123!",
            "rol": "ADMIN",
        }
        resp = self.client.post("/api/auth/registro", data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", resp.data)
        self.assertEqual(resp.data["usuario"]["rol"], "ADMIN")

    def test_registro_correo_duplicado(self):
        UsuarioModel.objects.create(
            correo="dup@test.com",
            password_hash=make_password("Pass123!"),
            rol="ADMIN",
        )
        resp = self.client.post(
            "/api/auth/registro",
            {"correo": "dup@test.com", "password": "Pass123!", "rol": "ADMIN"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errores", resp.data)

    def test_login_exitoso(self):
        UsuarioModel.objects.create(
            correo="login@test.com",
            password_hash=make_password("Pass123!"),
            rol="ADMIN",
        )
        resp = self.client.post(
            "/api/auth/login",
            {"correo": "login@test.com", "password": "Pass123!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("token", resp.data)

    def test_login_credenciales_invalidas(self):
        resp = self.client.post(
            "/api/auth/login",
            {"correo": "noexiste@test.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_perfil_con_token_valido(self):
        UsuarioModel.objects.create(
            correo="perfil@test.com",
            password_hash=make_password("Pass123!"),
            rol="ADMIN",
        )
        token = _get_token(self.client, "perfil@test.com", "Pass123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get("/api/auth/perfil")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["correo"], "perfil@test.com")

    def test_perfil_sin_token_retorna_401(self):
        resp = self.client.get("/api/auth/perfil")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class RolePermissionTests(TestCase):
    """Módulo 4 — Permisos por rol en endpoints de empleados."""

    def setUp(self):
        self.client = APIClient()
        self.compania = CompaniaModel.objects.create(
            nombre="Cia Roles", direccion="Dir", telefono="000"
        )
        self.empleado = EmpleadoModel.objects.create(
            nombre="Test", apellido="Rol", correo="emp@rol.com",
            cargo="Dev", salario=1000, compania=self.compania
        )
        # ADMIN
        UsuarioModel.objects.create(
            correo="admin@rol.com",
            password_hash=make_password("Admin123!"),
            rol="ADMIN",
        )
        # USUARIO de otra compañía (no propietario)
        otra = CompaniaModel.objects.create(nombre="Otra", direccion="X", telefono="1")
        UsuarioModel.objects.create(
            correo="user@otra.com",
            password_hash=make_password("User123!"),
            rol="USUARIO",
            compania=otra,
        )

    def _auth(self, correo, password):
        token = _get_token(self.client, correo, password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_admin_puede_eliminar_empleado(self):
        self._auth("admin@rol.com", "Admin123!")
        resp = self.client.delete(f"/api/empleados/{self.empleado.pk}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_usuario_no_puede_eliminar_empleado(self):
        """USUARIO no tiene permiso DELETE — solo ADMIN."""
        self._auth("user@otra.com", "User123!")
        resp = self.client.delete(f"/api/empleados/{self.empleado.pk}")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_sin_token_get_lista_retorna_401(self):
        self.client.credentials()
        resp = self.client.get("/api/empleados")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sin_token_get_companias_empleados_retorna_401(self):
        self.client.credentials()
        resp = self.client.get(f"/api/companias/{self.compania.pk}/empleados")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_con_token_get_companias_empleados_retorna_200(self):
        self._auth("user@otra.com", "User123!")
        resp = self.client.get(f"/api/companias/{self.compania.pk}/empleados")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class EsPropietarioDeCompaniaTests(TestCase):
    """Módulo 5 — Política EsPropietarioDeCompania."""

    def setUp(self):
        self.client = APIClient()
        self.cia1 = CompaniaModel.objects.create(nombre="Cia1", direccion="Dir1", telefono="1")
        self.cia2 = CompaniaModel.objects.create(nombre="Cia2", direccion="Dir2", telefono="2")

        self.emp_cia1 = EmpleadoModel.objects.create(
            nombre="Emp", apellido="Uno", correo="emp1@cia1.com",
            cargo="Dev", salario=2000, compania=self.cia1
        )
        # ADMIN (puede todo)
        UsuarioModel.objects.create(
            correo="admin@policy.com", password_hash=make_password("Admin!"), rol="ADMIN"
        )
        # USUARIO de cia1 (propietario)
        UsuarioModel.objects.create(
            correo="user@cia1.com", password_hash=make_password("User!"),
            rol="USUARIO", compania=self.cia1
        )
        # USUARIO de cia2 (no propietario)
        UsuarioModel.objects.create(
            correo="user@cia2.com", password_hash=make_password("User!"),
            rol="USUARIO", compania=self.cia2
        )

    def _auth(self, correo, password):
        token = _get_token(self.client, correo, password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_admin_puede_patch_cualquier_empleado(self):
        self._auth("admin@policy.com", "Admin!")
        resp = self.client.patch(
            f"/api/empleados/{self.emp_cia1.pk}",
            {"cargo": "Senior"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_usuario_propietario_puede_patch(self):
        self._auth("user@cia1.com", "User!")
        resp = self.client.patch(
            f"/api/empleados/{self.emp_cia1.pk}",
            {"cargo": "Junior"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_usuario_no_propietario_no_puede_patch(self):
        """Usuario de cia2 no puede modificar empleados de cia1."""
        self._auth("user@cia2.com", "User!")
        resp = self.client.patch(
            f"/api/empleados/{self.emp_cia1.pk}",
            {"cargo": "Hacker"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_propietario_no_puede_mover_empleado_a_otra_compania(self):
        """Un usuario con rol USUARIO no puede cambiar el compania_id de su empleado."""
        self._auth("user@cia1.com", "User!")
        resp = self.client.patch(
            f"/api/empleados/{self.emp_cia1.pk}",
            {"compania_id": self.cia2.pk}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_no_puede_crear_empleado_en_otra_compania(self):
        """Un usuario con rol USUARIO no puede crear un empleado en otra compañía."""
        self._auth("user@cia1.com", "User!")
        resp = self.client.post(
            "/api/empleados",
            {
                "nombre": "Nuevo",
                "apellido": "Emp",
                "correo": "nuevo.emp.cia2@test.com",
                "cargo": "Dev",
                "salario": "2000.00",
                "compania_id": self.cia2.pk
            },
            format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_puede_crear_empleado_en_su_compania(self):
        """Un usuario con rol USUARIO puede crear un empleado en su propia compañía."""
        self._auth("user@cia1.com", "User!")
        resp = self.client.post(
            "/api/empleados",
            {
                "nombre": "Nuevo",
                "apellido": "Emp",
                "correo": "nuevo.emp.cia1@test.com",
                "cargo": "Dev",
                "salario": "2000.00",
                "compania_id": self.cia1.pk
            },
            format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class PoliticaAdminCiudadTests(TestCase):
    """Política por claim ciudad: Medellín CRUD completo, Bogotá sin DELETE."""

    def setUp(self):
        self.client = APIClient()
        self.compania = CompaniaModel.objects.create(
            nombre="Cia Ciudad", direccion="Dir", telefono="000"
        )
        self.empleado = EmpleadoModel.objects.create(
            nombre="Emp", apellido="Ciudad", correo="emp@ciudad.com",
            cargo="Dev", salario=1000, compania=self.compania,
        )
        UsuarioModel.objects.create(
            correo="admin.med@ciudad.com",
            password_hash=make_password("Admin123!"),
            rol="ADMIN",
            ciudad="Medellín",
        )
        UsuarioModel.objects.create(
            correo="admin.bog@ciudad.com",
            password_hash=make_password("Admin123!"),
            rol="ADMIN",
            ciudad="Bogotá",
        )

    def _auth(self, correo):
        token = _get_token(self.client, correo, "Admin123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_admin_medellin_puede_eliminar(self):
        self._auth("admin.med@ciudad.com")
        resp = self.client.delete(f"/api/empleados/{self.empleado.pk}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_bogota_no_puede_eliminar(self):
        self._auth("admin.bog@ciudad.com")
        resp = self.client.delete(f"/api/empleados/{self.empleado.pk}")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_bogota_puede_crear_empleado(self):
        self._auth("admin.bog@ciudad.com")
        resp = self.client.post(
            "/api/empleados",
            {
                "nombre": "Nuevo",
                "apellido": "Bog",
                "correo": "nuevo@bog.com",
                "cargo": "Dev",
                "salario": "2000",
                "compania_id": self.compania.pk,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_login_incluye_ciudad_en_respuesta(self):
        resp = self.client.post(
            "/api/auth/login",
            {"correo": "admin.bog@ciudad.com", "password": "Admin123!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["usuario"]["ciudad"], "Bogotá")
        self.assertIn("token", resp.data)


class BulkEmpleadoPermissionTests(TestCase):
    """
    Módulo 5 — Política EsPropietarioDeCompania en creación masiva (bulk).

    Verifica que POST /api/empleados/bulk aplique correctamente la política
    de propiedad: un USUARIO solo puede crear empleados en su propia compañía.
    """

    def setUp(self):
        self.client = APIClient()
        self.cia1 = CompaniaModel.objects.create(nombre="CiaBulk1", direccion="Dir1", telefono="1")
        self.cia2 = CompaniaModel.objects.create(nombre="CiaBulk2", direccion="Dir2", telefono="2")

        # ADMIN (puede crear en cualquier compañía)
        UsuarioModel.objects.create(
            correo="admin@bulk.com",
            password_hash=make_password("Admin123!"),
            rol="ADMIN",
        )
        # USUARIO de cia1
        UsuarioModel.objects.create(
            correo="user@bulk1.com",
            password_hash=make_password("User123!"),
            rol="USUARIO",
            compania=self.cia1,
        )
        # USUARIO de cia2
        UsuarioModel.objects.create(
            correo="user@bulk2.com",
            password_hash=make_password("User123!"),
            rol="USUARIO",
            compania=self.cia2,
        )

    def _auth(self, correo, password):
        token = _get_token(self.client, correo, password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_admin_puede_crear_bulk_en_cualquier_compania(self):
        """ADMIN puede crear empleados en cualquier compañía con bulk."""
        self._auth("admin@bulk.com", "Admin123!")
        payload = {
            "empleados": [
                {
                    "nombre": "A", "apellido": "Uno", "correo": "a.uno@bulk.com",
                    "cargo": "Dev", "salario": "1000.00", "compania_id": self.cia1.pk,
                },
                {
                    "nombre": "B", "apellido": "Dos", "correo": "b.dos@bulk.com",
                    "cargo": "QA", "salario": "1200.00", "compania_id": self.cia2.pk,
                },
            ]
        }
        resp = self.client.post("/api/empleados/bulk", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data), 2)

    def test_usuario_propietario_puede_crear_bulk_en_su_compania(self):
        """USUARIO puede crear bulk solo en su propia compañía."""
        self._auth("user@bulk1.com", "User123!")
        payload = {
            "empleados": [
                {
                    "nombre": "C", "apellido": "Tres", "correo": "c.tres@bulk.com",
                    "cargo": "Dev", "salario": "1500.00", "compania_id": self.cia1.pk,
                },
                {
                    "nombre": "D", "apellido": "Cuatro", "correo": "d.cuatro@bulk.com",
                    "cargo": "PM", "salario": "1800.00", "compania_id": self.cia1.pk,
                },
            ]
        }
        resp = self.client.post("/api/empleados/bulk", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data), 2)

    def test_usuario_no_puede_crear_bulk_en_otra_compania(self):
        """USUARIO de cia1 recibe 403 si intenta crear empleados en cia2."""
        self._auth("user@bulk1.com", "User123!")
        payload = {
            "empleados": [
                {
                    "nombre": "E", "apellido": "Cinco", "correo": "e.cinco@bulk.com",
                    "cargo": "Dev", "salario": "1000.00", "compania_id": self.cia2.pk,
                },
            ]
        }
        resp = self.client.post("/api/empleados/bulk", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_no_puede_crear_bulk_con_lista_mixta(self):
        """USUARIO de cia1 recibe 403 si una de las entradas bulk es de cia2."""
        self._auth("user@bulk1.com", "User123!")
        payload = {
            "empleados": [
                {
                    "nombre": "F", "apellido": "Seis", "correo": "f.seis@bulk.com",
                    "cargo": "Dev", "salario": "1000.00", "compania_id": self.cia1.pk,
                },
                {
                    "nombre": "G", "apellido": "Siete", "correo": "g.siete@bulk.com",
                    "cargo": "QA", "salario": "1200.00", "compania_id": self.cia2.pk,
                },
            ]
        }
        resp = self.client.post("/api/empleados/bulk", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_sin_token_bulk_retorna_401(self):
        """Sin token, el endpoint bulk devuelve 401."""
        self.client.credentials()
        payload = {
            "empleados": [
                {
                    "nombre": "H", "apellido": "Ocho", "correo": "h.ocho@bulk.com",
                    "cargo": "Dev", "salario": "1000.00", "compania_id": self.cia1.pk,
                }
            ]
        }
        resp = self.client.post("/api/empleados/bulk", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


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

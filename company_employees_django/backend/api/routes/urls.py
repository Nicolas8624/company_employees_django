"""
Configuración de URLs para la API REST.

Define todos los endpoints de compañías y empleados.
"""
from django.urls import path

from api.controllers.compania_controller import (
    CompaniaConEmpleadosController,
    CompaniaDetailController,
    CompaniaEmpleadosController,
    CompaniaListController,
)
from api.controllers.empleado_controller import (
    EmpleadoDetailController,
    EmpleadoListController,
    EmpleadoBulkController,
)
from api.controllers.auth_controller import (
    RegistroController,
    LoginController,
    PerfilController,
)

urlpatterns = [
    # === Auth ===
    path("auth/registro", RegistroController.as_view(), name="auth-registro"),
    path("auth/login", LoginController.as_view(), name="auth-login"),
    path("auth/perfil", PerfilController.as_view(), name="auth-perfil"),

    # === Compañías ===
    # GET/POST /api/companias
    path("companias", CompaniaListController.as_view(), name="compania-list"),
    # GET/PUT/DELETE /api/companias/{id}
    path("companias/<int:pk>", CompaniaDetailController.as_view(), name="compania-detail"),
    # GET /api/companias/{id}/empleados
    path(
        "companias/<int:pk>/empleados",
        CompaniaEmpleadosController.as_view(),
        name="compania-empleados",
    ),
    # POST /api/companias/con-empleados (TRANSACCIONAL)
    path(
        "companias/con-empleados",
        CompaniaConEmpleadosController.as_view(),
        name="compania-con-empleados",
    ),

    # === Empleados ===
    # GET/POST /api/empleados
    path("empleados", EmpleadoListController.as_view(), name="empleado-list"),
    # POST/DELETE /api/empleados/bulk
    path("empleados/bulk", EmpleadoBulkController.as_view(), name="empleado-bulk"),
    path("empleados/bulk-delete", EmpleadoBulkController.as_view(), name="empleado-bulk-delete"),
    # GET/PUT/PATCH/DELETE /api/empleados/{id}
    path("empleados/<int:pk>", EmpleadoDetailController.as_view(), name="empleado-detail"),
]

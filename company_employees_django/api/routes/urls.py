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
)

urlpatterns = [
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
    # GET/PUT/DELETE /api/empleados/{id}
    path("empleados/<int:pk>", EmpleadoDetailController.as_view(), name="empleado-detail"),
]

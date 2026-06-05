"""
Controller para Empleados.

Maneja las peticiones HTTP y delega TODA la lógica de negocio
al EmpleadoService. NO accede al ORM directamente.

Flujo: Controller → Service → UnitOfWork → Repository → ORM → Database

Usa ServiceLocator para obtener los servicios sin conocer
las implementaciones concretas de Infrastructure.
"""
import logging
from dataclasses import asdict

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.empleado_serializer import (
    EmpleadoCreateSerializer,
    EmpleadoSerializer,
    EmpleadoPatchSerializer,
    EmpleadoBulkCreateSerializer,
    BulkDeleteSerializer,
)
from api.permissions.permissions import (
    IsAdmin,
    IsAdminOrUsuario,
    IsAuthenticatedUser,
    EsPropietarioDeCompania,
    PoliticaAdminCiudad,
)
from domain.exceptions import DomainValidationError
from infrastructure.service_locator import ServiceLocator

logger = logging.getLogger(__name__)


class EmpleadoListController(APIView):
    """
    GET /api/empleados     → Listar todos los empleados [autenticado]
    POST /api/empleados    → Crear nuevo empleado [ADMIN o USUARIO]
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedUser()]
        return [IsAdminOrUsuario(), EsPropietarioDeCompania(), PoliticaAdminCiudad()]

    def get(self, request: Request) -> Response:
        """Listar todos los empleados (con paginación)."""
        logger.info("GET /api/empleados")
        service = ServiceLocator.get_empleado_service()
        
        page = int(request.query_params.get("pagina", 1))
        size = int(request.query_params.get("tamano", 10))
        sort_by = request.query_params.get("orden", "")
        sort_dir = request.query_params.get("dir", "asc")
        search = request.query_params.get("buscar", "")
        
        paginated = service.get_paginated_empleados(
            page=page, size=size, sort_by=sort_by, sort_dir=sort_dir, search=search
        )
        
        serializer = EmpleadoSerializer(
            [asdict(e) for e in paginated["datos"]], many=True
        )
        
        paginated["datos"] = serializer.data
        return Response(paginated, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Crear un nuevo empleado."""
        logger.info("POST /api/empleados")
        serializer = EmpleadoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ServiceLocator.get_empleado_service()
            empleado = service.create_empleado(serializer.validated_data)
            response_serializer = EmpleadoSerializer(asdict(empleado))
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED
            )
        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST
            )


class EmpleadoDetailController(APIView):
    """
    GET    /api/empleados/{id}  → Obtener empleado [autenticado]
    PUT    /api/empleados/{id}  → Actualizar empleado [ADMIN o USUARIO + propietario]
    PATCH  /api/empleados/{id}  → Patch parcial [ADMIN o USUARIO + propietario]
    DELETE /api/empleados/{id}  → Eliminar empleado [solo ADMIN]
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedUser()]
        if self.request.method == 'DELETE':
            return [IsAdmin(), PoliticaAdminCiudad()]
        # PUT / PATCH: requiere autenticación + ser propietario de la compañía + política de ciudad
        return [IsAdminOrUsuario(), EsPropietarioDeCompania(), PoliticaAdminCiudad()]

    def get(self, request: Request, pk: int) -> Response:
        """Obtener un empleado por su ID."""
        logger.info("GET /api/empleados/%s", pk)
        service = ServiceLocator.get_empleado_service()
        empleado = service.get_empleado_by_id(pk)
        if empleado is None:
            return Response(
                {"error": "Empleado no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmpleadoSerializer(asdict(empleado))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, pk: int) -> Response:
        """Actualizar un empleado existente."""
        logger.info("PUT /api/empleados/%s", pk)

        # Verificar política de propiedad a nivel de objeto
        service = ServiceLocator.get_empleado_service()
        empleado_existente = service.get_empleado_by_id(pk)
        if empleado_existente is None:
            return Response(
                {"error": "Empleado no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, empleado_existente)

        serializer = EmpleadoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            empleado = service.update_empleado(pk, serializer.validated_data)
            response_serializer = EmpleadoSerializer(asdict(empleado))
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request: Request, pk: int) -> Response:
        """Actualización parcial de un empleado."""
        logger.info("PATCH /api/empleados/%s", pk)

        # Verificar política de propiedad a nivel de objeto
        service = ServiceLocator.get_empleado_service()
        empleado_existente = service.get_empleado_by_id(pk)
        if empleado_existente is None:
            return Response(
                {"error": "Empleado no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, empleado_existente)

        serializer = EmpleadoPatchSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            empleado = service.patch_empleado(pk, serializer.validated_data)
            response_serializer = EmpleadoSerializer(asdict(empleado))
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, pk: int) -> Response:
        """Eliminar un empleado."""
        logger.info("DELETE /api/empleados/%s", pk)
        service = ServiceLocator.get_empleado_service()
        deleted = service.delete_empleado(pk)
        if not deleted:
            return Response(
                {"error": "Empleado no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmpleadoBulkController(APIView):
    """
    POST /api/empleados/bulk          → Crear múltiples [ADMIN o USUARIO]
    DELETE /api/empleados/bulk-delete  → Eliminar múltiples [solo ADMIN]
    """

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin(), PoliticaAdminCiudad()]
        return [IsAdminOrUsuario(), EsPropietarioDeCompania(), PoliticaAdminCiudad()]

    def post(self, request: Request) -> Response:
        logger.info("POST /api/empleados/bulk")
        serializer = EmpleadoBulkCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = ServiceLocator.get_empleado_service()
            empleados = service.bulk_create_empleados(serializer.validated_data["empleados"])
            response_serializer = EmpleadoSerializer([asdict(e) for e in empleados], many=True)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except DomainValidationError as e:
            return Response({"errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request) -> Response:
        logger.info("DELETE /api/empleados/bulk-delete")
        serializer = BulkDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = ServiceLocator.get_empleado_service()
        count = service.delete_many_empleados(serializer.validated_data["ids"])
        return Response({"eliminados": count}, status=status.HTTP_200_OK)

"""
Controller para Compañías.

Maneja las peticiones HTTP y delega TODA la lógica de negocio
al CompaniaService. NO accede al ORM directamente.

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

from api.serializers.compania_serializer import (
    CompaniaCreateSerializer,
    CompaniaSerializer,
    CompaniaPatchSerializer,
)
from api.serializers.compania_con_empleados_serializer import (
    CompaniaConEmpleadosSerializer,
)
from api.serializers.empleado_serializer import EmpleadoSerializer
from api.permissions.permissions import (
    IsAdmin,
    IsAdminOrUsuario,
    IsAuthenticatedUser,
    PoliticaAdminCiudad,
)
from domain.exceptions import DomainValidationError
from infrastructure.service_locator import ServiceLocator

logger = logging.getLogger(__name__)


class CompaniaListController(APIView):
    """
    GET /api/companias     → Listar compañías [autenticado]
    POST /api/companias    → Crear compañía [ADMIN o USUARIO]
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedUser()]
        return [IsAdminOrUsuario(), PoliticaAdminCiudad()]

    def get(self, request: Request) -> Response:
        """Listar todas las compañías (con paginación)."""
        logger.info("GET /api/companias")
        service = ServiceLocator.get_compania_service()
        
        page = int(request.query_params.get("pagina", 1))
        size = int(request.query_params.get("tamano", 10))
        sort_by = request.query_params.get("orden", "")
        sort_dir = request.query_params.get("dir", "asc")
        search = request.query_params.get("buscar", "")
        
        paginated = service.get_paginated_companias(
            page=page, size=size, sort_by=sort_by, sort_dir=sort_dir, search=search
        )
        
        serializer = CompaniaSerializer(
            [asdict(c) for c in paginated["datos"]], many=True
        )
        paginated["datos"] = serializer.data
        return Response(paginated, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Crear una nueva compañía."""
        logger.info("POST /api/companias")
        serializer = CompaniaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ServiceLocator.get_compania_service()
            compania = service.create_compania(serializer.validated_data)
            response_serializer = CompaniaSerializer(asdict(compania))
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED
            )
        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST
            )


class CompaniaDetailController(APIView):
    """
    GET    /api/companias/{id}  → Obtener compañía [autenticado]
    PUT    /api/companias/{id}  → Actualizar [ADMIN o USUARIO]
    PATCH  /api/companias/{id}  → Patch parcial [ADMIN o USUARIO]
    DELETE /api/companias/{id}  → Eliminar [solo ADMIN]
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedUser()]
        if self.request.method == 'DELETE':
            return [IsAdmin(), PoliticaAdminCiudad()]
        return [IsAdminOrUsuario(), PoliticaAdminCiudad()]

    def get(self, request: Request, pk: int) -> Response:
        """Obtener una compañía por su ID."""
        logger.info("GET /api/companias/%s", pk)
        service = ServiceLocator.get_compania_service()
        compania = service.get_compania_by_id(pk)
        if compania is None:
            return Response(
                {"error": "Compañía no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompaniaSerializer(asdict(compania))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, pk: int) -> Response:
        """Actualizar una compañía existente."""
        logger.info("PUT /api/companias/%s", pk)
        serializer = CompaniaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ServiceLocator.get_compania_service()
            compania = service.update_compania(pk, serializer.validated_data)
            if compania is None:
                return Response(
                    {"error": "Compañía no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response_serializer = CompaniaSerializer(asdict(compania))
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request: Request, pk: int) -> Response:
        """Actualizar parcialmente una compañía."""
        logger.info("PATCH /api/companias/%s", pk)
        serializer = CompaniaPatchSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ServiceLocator.get_compania_service()
            compania = service.patch_compania(pk, serializer.validated_data)
            if compania is None:
                return Response(
                    {"error": "Compañía no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response_serializer = CompaniaSerializer(asdict(compania))
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, pk: int) -> Response:
        """Eliminar una compañía."""
        logger.info("DELETE /api/companias/%s", pk)
        service = ServiceLocator.get_compania_service()
        deleted = service.delete_compania(pk)
        if not deleted:
            return Response(
                {"error": "Compañía no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompaniaEmpleadosController(APIView):
    """
    GET /api/companias/{id}/empleados → Obtener empleados de una compañía
    """

    def get(self, request: Request, pk: int) -> Response:
        """Obtener todos los empleados de una compañía."""
        logger.info("GET /api/companias/%s/empleados", pk)
        service = ServiceLocator.get_compania_service()
        empleados = service.get_empleados_by_compania(pk)
        if empleados is None:
            return Response(
                {"error": "Compañía no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmpleadoSerializer(
            [asdict(e) for e in empleados], many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompaniaConEmpleadosController(APIView):
    """
    POST /api/companias/con-empleados → Crear compañía + empleados [solo ADMIN]
    """

    permission_classes = [IsAdmin, PoliticaAdminCiudad]

    def post(self, request: Request) -> Response:
        """Crear compañía con empleados en una sola transacción."""
        logger.info("POST /api/companias/con-empleados — TRANSACCIONAL")
        serializer = CompaniaConEmpleadosSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ServiceLocator.get_compania_service()
            resultado = service.create_compania_con_empleados(
                serializer.validated_data
            )
            response_data = {
                "compania": CompaniaSerializer(asdict(resultado["compania"])).data,
                "empleados": EmpleadoSerializer(
                    [asdict(e) for e in resultado["empleados"]], many=True
                ).data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Error en transacción: %s", str(e))
            return Response(
                {"error": f"Error en la transacción: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

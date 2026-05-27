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
)
from domain.exceptions import DomainValidationError
from infrastructure.service_locator import ServiceLocator

logger = logging.getLogger(__name__)


class EmpleadoListController(APIView):
    """
    GET /api/empleados     → Listar todos los empleados
    POST /api/empleados    → Crear nuevo empleado
    """

    def get(self, request: Request) -> Response:
        """Listar todos los empleados."""
        logger.info("GET /api/empleados")
        service = ServiceLocator.get_empleado_service()
        empleados = service.get_all_empleados()
        serializer = EmpleadoSerializer(
            [asdict(e) for e in empleados], many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                {"error": e.mensaje}, status=status.HTTP_400_BAD_REQUEST
            )


class EmpleadoDetailController(APIView):
    """
    GET /api/empleados/{id}     → Obtener empleado por ID
    PUT /api/empleados/{id}     → Actualizar empleado
    DELETE /api/empleados/{id}  → Eliminar empleado
    """

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
        serializer = EmpleadoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Datos inválidos: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ServiceLocator.get_empleado_service()
            empleado = service.update_empleado(pk, serializer.validated_data)
            if empleado is None:
                return Response(
                    {"error": "Empleado no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response_serializer = EmpleadoSerializer(asdict(empleado))
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except DomainValidationError as e:
            logger.warning("Validación de dominio fallida: %s", e.mensaje)
            return Response(
                {"error": e.mensaje}, status=status.HTTP_400_BAD_REQUEST
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

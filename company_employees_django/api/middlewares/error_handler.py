"""
Middleware global para manejo de errores.

Captura excepciones no manejadas y las registra en el log,
devolviendo una respuesta JSON estandarizada.
"""
import logging
import traceback

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """Middleware que captura errores inesperados y los registra."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Capturar excepciones no manejadas."""
        logger.error(
            "Error inesperado en %s %s: %s",
            request.method,
            request.path,
            str(exception),
        )
        logger.error("Traceback:\n%s", traceback.format_exc())

        return JsonResponse(
            {
                "error": "Error interno del servidor",
                "detalle": str(exception),
            },
            status=500,
        )

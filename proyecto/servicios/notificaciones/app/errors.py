"""Errores estructurados: toda respuesta de error tiene la misma forma JSON

    {"error": {"code": "...", "message": "...", "details": {...}}}

para que el cliente (o el monolito) nunca tenga que parsear HTML ni adivinar.
"""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger("notificaciones")


class ApiError(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(ApiError):
    status_code = 400
    code = "VALIDATION_ERROR"


class UnsupportedChannelError(ApiError):
    status_code = 400
    code = "UNSUPPORTED_CHANNEL"


class DeliveryError(ApiError):
    """El proveedor externo no pudo entregar el mensaje."""

    status_code = 502
    code = "DELIVERY_FAILED"


def _body(code: str, message: str, details: dict | None = None):
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return jsonify(_body(err.code, err.message, err.details)), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(err: HTTPException):
        code = (err.name or "HTTP_ERROR").upper().replace(" ", "_")
        return jsonify(_body(code, err.description or err.name)), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        logger.exception("Error inesperado en el microservicio de notificaciones")
        return jsonify(_body("INTERNAL_ERROR", "Error interno del servicio de notificaciones.")), 500

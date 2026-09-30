"""Microservicio de Notificaciones (API v2).

Primer módulo estrangulado del monolito Django siguiendo el Strangler Pattern:
recibe peticiones JSON en /api/v2/notificaciones y entrega el mensaje por el
canal pedido (Email, SMS o WhatsApp). No comparte base de datos con el
monolito: su única entrada es el contrato HTTP.
"""
import logging

from flask import Flask

from .errors import register_error_handlers
from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    register_error_handlers(app)
    app.register_blueprint(bp)
    return app

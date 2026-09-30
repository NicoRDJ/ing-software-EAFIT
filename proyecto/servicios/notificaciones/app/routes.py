"""Rutas de la API v2. Nginx enruta /api/v2/notificaciones hacia este servicio,
así que la ruta declarada aquí es la ruta completa (no solo /notificaciones)."""
import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from .errors import DeliveryError
from .notifiers import NotifierFactory
from .validation import parse_notification

bp = Blueprint("notificaciones", __name__, url_prefix="/api/v2/notificaciones")


@bp.post("")
@bp.post("/")
def enviar_notificacion():
    data = parse_notification(request.get_json(silent=True))
    notifier = NotifierFactory.create(data["channel"])

    if not notifier.send(data["recipient"], data["message"]):
        raise DeliveryError("El proveedor no pudo entregar la notificación.", {"channel": data["channel"]})

    return jsonify({
        "id": str(uuid.uuid4()),
        "status": "ENVIADA",
        **data,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "service": "notificaciones-flask (v2)",
    }), 201


@bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "notificaciones-flask (v2)", "channels": NotifierFactory.channels()})

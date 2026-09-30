from unittest import mock

import pytest
from app.notifiers import EmailNotifier

URL = "/api/v2/notificaciones"


def test_envio_email_exitoso_responde_201_con_json(client):
    resp = client.post(URL, json={"channel": "EMAIL", "recipient": "cliente@correo.com", "message": "Tu licencia"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["status"] == "ENVIADA"
    assert body["channel"] == "EMAIL"
    assert body["notification_type"] == "ORDER_CONFIRMATION"
    assert body["id"] and body["sent_at"]


@pytest.mark.parametrize("channel,recipient", [("SMS", "+573001234567"), ("whatsapp", "3001234567")])
def test_canales_telefonicos(client, channel, recipient):
    resp = client.post(URL, json={"channel": channel, "recipient": recipient, "message": "Hola"})
    assert resp.status_code == 201
    assert resp.get_json()["channel"] == channel.upper()


def test_canal_no_soportado_responde_400_estructurado(client):
    resp = client.post(URL, json={"channel": "FAX", "recipient": "x", "message": "y"})
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "UNSUPPORTED_CHANNEL"


def test_campos_invalidos_devuelve_detalle_por_campo(client):
    resp = client.post(URL, json={"channel": "EMAIL", "recipient": "no-es-correo", "message": ""})
    assert resp.status_code == 400
    error = resp.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert set(error["details"]) == {"recipient", "message"}


def test_cuerpo_que_no_es_json_responde_400(client):
    resp = client.post(URL, data="texto plano", content_type="text/plain")
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_fallo_del_proveedor_responde_502(client):
    with mock.patch.object(EmailNotifier, "send", return_value=False):
        resp = client.post(URL, json={"channel": "EMAIL", "recipient": "a@b.co", "message": "x"})
    assert resp.status_code == 502
    assert resp.get_json()["error"]["code"] == "DELIVERY_FAILED"


def test_error_inesperado_responde_500_json(client):
    with mock.patch.object(EmailNotifier, "send", side_effect=RuntimeError("boom")):
        resp = client.post(URL, json={"channel": "EMAIL", "recipient": "a@b.co", "message": "x"})
    assert resp.status_code == 500
    assert resp.get_json()["error"]["code"] == "INTERNAL_ERROR"


def test_metodo_no_permitido_tambien_es_json(client):
    resp = client.get(URL)
    assert resp.status_code == 405
    assert "error" in resp.get_json()


def test_health(client):
    resp = client.get(URL + "/health")
    assert resp.status_code == 200
    assert resp.get_json()["channels"] == ["EMAIL", "SMS", "WHATSAPP"]

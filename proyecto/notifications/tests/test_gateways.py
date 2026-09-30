import json
from unittest import mock

from django.test import SimpleTestCase, override_settings

from common.exceptions import UnsupportedNotificationChannelError
from notifications.factories import NotificationFactory
from notifications.gateways import RemoteNotifier, RemoteNotifierFactory, default_notification_factory


class _FakeResponse:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class RemoteNotifierTests(SimpleTestCase):
    def test_envia_json_al_endpoint_v2(self):
        with mock.patch("urllib.request.urlopen", return_value=_FakeResponse(201)) as urlopen:
            ok = RemoteNotifier("http://notificaciones_flask:5000/", "EMAIL").send("a@b.co", "hola")
        self.assertTrue(ok)
        req = urlopen.call_args.args[0]
        self.assertEqual(req.full_url, "http://notificaciones_flask:5000/api/v2/notificaciones")
        self.assertEqual(json.loads(req.data), {"channel": "EMAIL", "recipient": "a@b.co", "message": "hola"})

    def test_servicio_caido_devuelve_false_sin_romper_la_orden(self):
        import urllib.error

        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("down")):
            self.assertFalse(RemoteNotifier("http://x:5000", "SMS").send("+573001234567", "hola"))

    @override_settings(NOTIFICATIONS_SERVICE_URL="http://notificaciones_flask:5000")
    def test_factory_remota_rechaza_canal_desconocido(self):
        with self.assertRaises(UnsupportedNotificationChannelError):
            RemoteNotifierFactory.create("FAX")


class DefaultFactoryTests(SimpleTestCase):
    @override_settings(NOTIFICATIONS_SERVICE_URL="")
    def test_sin_url_usa_envio_in_process(self):
        self.assertIs(default_notification_factory(), NotificationFactory)

    @override_settings(NOTIFICATIONS_SERVICE_URL="http://notificaciones_flask:5000")
    def test_con_url_delega_al_microservicio(self):
        self.assertIs(default_notification_factory(), RemoteNotifierFactory)

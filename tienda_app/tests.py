import os
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from .domain.builders import OrdenBuilder
from .infra.factories import MockPaymentProcessor, PaymentFactory
from .infra.gateways import BancoNacionalProcesador
from .models import Inventario, Libro


class PaymentFactoryTests(TestCase):
    def test_mock_desde_variable_de_entorno(self):
        with mock.patch.dict(os.environ, {"PAYMENT_PROVIDER": "MOCK"}):
            self.assertIsInstance(PaymentFactory.get_processor(), MockPaymentProcessor)

    def test_banco_por_defecto(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsInstance(PaymentFactory.get_processor(), BancoNacionalProcesador)


class OrdenBuilderTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("ana", password="x")
        self.libro = Libro.objects.create(titulo="Clean Architecture", precio=Decimal("180.00"))

    def test_build_calcula_total_con_iva(self):
        orden = OrdenBuilder().con_usuario(self.usuario).con_productos([self.libro]).para_envio("Calle 10").build()
        self.assertEqual(orden.total, Decimal("214.20"))
        self.assertEqual(orden.direccion_envio, "Calle 10")

    def test_build_sin_usuario_falla(self):
        with self.assertRaises(ValueError):
            OrdenBuilder().con_productos([self.libro]).build()

    def test_build_sin_productos_falla(self):
        with self.assertRaises(ValueError):
            OrdenBuilder().con_usuario(self.usuario).build()

    def test_reset_tras_build(self):
        builder = OrdenBuilder()
        builder.con_usuario(self.usuario).con_productos([self.libro]).build()
        with self.assertRaises(ValueError):
            builder.build()


class CompraViewTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("ana", password="x")
        self.libro = Libro.objects.create(titulo="DDD", precio=Decimal("210.00"))
        Inventario.objects.create(libro=self.libro, cantidad=2)

    @mock.patch.dict(os.environ, {"PAYMENT_PROVIDER": "MOCK"})
    def test_compra_con_mock_descuenta_stock(self):
        self.client.force_login(self.usuario)
        resp = self.client.post(f"/compra/{self.libro.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Inventario.objects.get(libro=self.libro).cantidad, 1)

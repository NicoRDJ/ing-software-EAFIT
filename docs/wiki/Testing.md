# Testing

## Cómo correr

```bash
python manage.py test          # todos los tests
python manage.py test sales    # solo una app
python manage.py test -v 2     # verboso, un renglón por test
```

**Resultado real de la última corrida completa: 40/40 tests pasando (`Ran 40 tests ... OK`).**

## Estrategia

| Tipo | Dónde | Qué cubre |
|---|---|---|
| Unitarios de Builder | `sales/tests/test_builders.py` (8 tests) | Invariantes de `OrderBuilder` sin tocar la base de datos: sin cliente, sin ítems, cantidad inválida, cálculo de total con y sin cupón, cupón vencido/inactivo |
| Unitarios de Factory | `notifications/tests/test_factories.py` (5 tests) | `NotificationFactory` devuelve el `Notifier` correcto por canal; canal desconocido levanta `UnsupportedNotificationChannelError` |
| Unitario de DI | `notifications/tests/test_services.py` (1 test) | `NotificationService` puede recibir una factory falsa por constructor y nunca invoca un `Notifier` real |
| Servicios (integración con DB) | `sales/tests/test_services.py` (6 tests), `licensing/tests/test_services.py` (4 tests) | Camino feliz de checkout, rollback real en stock insuficiente, conflicto de doble pago, límite de activaciones |
| API (`APITestCase`, HTTP real vía test client de DRF) | `sales/tests/test_api.py` (9 tests), `licensing/tests/test_api.py` (5 tests), `sales/tests/test_api.py::CustomerApiTests` | Los cuatro códigos de estado que pide el PDF: **201, 400, 404, 409** — en más de un endpoint cada uno |

## Cobertura explícita de códigos HTTP

| Código | Dónde se prueba |
|---|---|
| 201 | Crear pedido, crear cliente, crear clave de licencia |
| 400 | Pedido sin ítems, email duplicado, activación sin `device_fingerprint` |
| 404 | Pedido/producto/cliente/clave inexistente |
| 409 | Stock insuficiente, doble pago, activación fuera de límite, activación de clave no vendida |

## Qué se mockea y por qué

Solo `notifications/tests/test_services.py` usa un doble de prueba (`_RecordingNotifier` + `_FakeFactory`), y únicamente para demostrar que `NotificationService` es sustituible sin tocar un proveedor real — es la respuesta concreta a "¿puedo testear el service sin enviar una notificación real?" (sí). El resto de los tests usa la base de datos de pruebas real de Django (SQLite en memoria) sin mocks: las reglas de `LicenseAllocationService`, `PaymentService` y `ActivationService` dependen de consultas reales entre tablas, y mockear el ORM ahí habría probado menos que dejarlo correr contra una base real — que además es rápida (los 40 tests corren en bajo un segundo).

## Verificación manual adicional

Además de la suite automatizada, el flujo completo (`products` → `orders` → `pay` → `activate`, incluyendo los casos 400/404/409) se ejecutó contra `python manage.py runserver` real con `curl`, no solo con el test client — ver el reporte de auditoría final de la entrega para el detalle de esa corrida.

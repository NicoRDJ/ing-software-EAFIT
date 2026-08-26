# Architecture

## Estructura de carpetas

```
config/            Proyecto Django: settings.py, urls.py raíz, wsgi/asgi
common/             Excepciones de dominio + exception handler de DRF (sin modelos, no es una app registrada)
catalog/            SoftwareProduct
licensing/           LicenseKey, ActivationRecord, ActivationService
sales/               Customer, Order, OrderItem, Coupon, Payment, OrderBuilder, OrderService/PaymentService/LicenseAllocationService
notifications/       Notification, Notifier(s), NotificationFactory, NotificationService
docs/wiki/           Este contenido
```

## Por qué apps por contexto acotado, y no capas horizontales

Se evaluaron dos formas de organizar el proyecto:

1. **Capas horizontales** (`models/`, `services/`, `views/`, `serializers/` como carpetas de primer nivel con todo mezclado adentro).
2. **Apps por contexto de negocio** (`catalog`, `licensing`, `sales`, `notifications`), cada una con su propio `models.py`, `services.py`, `serializers.py`, `views.py`, `urls.py`.

Se eligió la segunda porque:

- Es la convención nativa de Django (cada app es instalable, migrable y testeable de forma independiente) — no se está peleando contra el framework.
- El acoplamiento entre contextos queda explícito en los imports: `sales` importa de `licensing` (necesita `LicenseType`), pero `licensing` **no** importa el módulo de `sales` directamente — usa una referencia perezosa por string (`"sales.OrderItem"`) en su único FK hacia `sales`. Esa asimetría está documentada en el propio código (`licensing/models.py`) porque es la única forma de evitar un import circular real entre ambas apps.
- `notifications` no depende de `sales` para nada de tipos/choices — `sales.models.DeliveryChannel` está deliberadamente duplicado (no importado) para que `sales` no tenga que conocer `notifications` en absoluto. El acoplamiento entre ambos ocurre solo en la capa de servicios (`OrderService` usa `NotificationService`), que es donde se espera que ocurra la orquestación entre contextos — no en los modelos.

## `common/` no es una app Django

`common/exceptions.py` y `common/drf_exception_handler.py` no tienen modelos ni necesitan migraciones, así que no está en `INSTALLED_APPS` — es un paquete Python normal que las demás apps importan. Forzarlo a ser una "app" habría sido ceremonia sin beneficio.

## Dónde vive cada tipo de código

| Carpeta/archivo | Contiene | No contiene |
|---|---|---|
| `models.py` | Campos, validators de un solo campo, invariantes puros sobre las propias columnas del modelo (ej. `Coupon.is_valid_now()`) | Reglas que requieran consultar otras filas/tablas |
| `services.py` | Casos de uso completos: orquestación, reglas cruzadas entre entidades, transacciones | Parsing de HTTP, serialización |
| `builders.py` | Construcción paso a paso de un agregado complejo, validado antes de existir | Persistencia (`.objects.create()`) |
| `factories.py` / `notifiers.py` | Selección/creación de una implementación intercambiable | Cuándo o por qué se envía algo (eso es de `services.py`) |
| `serializers.py` | Contratos de entrada/salida, validación de formato | Lógica de negocio |
| `views.py` | Recibir request → validar con serializer → llamar service → responder | Cualquier `if` que exprese una regla de negocio |

## Flujo de una dependencia típica

```
views.py  ->  serializers.py (valida forma)
views.py  ->  services.py (ejecuta el caso de uso)
services.py -> builders.py / models.py / otros services.py
services.py -> se le escapan excepciones de dominio (common/exceptions.py)
Excepción no atrapada -> common/drf_exception_handler.py -> Response HTTP
```

Ninguna vista atrapa una excepción de dominio manualmente — todas se resuelven en el exception handler centralizado (ver [Service-Layer](Service-Layer.md)).

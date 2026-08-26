# Design Patterns

## Builder — `sales/builders.py::OrderBuilder`

### Problema

`Order` es el agregado más complejo del sistema: requiere un cliente obligatorio, un número variable de líneas (cada una con su propio producto, tipo de licencia y cantidad), un cupón opcional que **solo es válido si está vigente y activo**, un canal de entrega, y un total que debe calcularse de forma consistente a partir de todo lo anterior — antes de que exista ninguna fila en la base de datos. Construirlo con un `Order.objects.create(**kwargs)` directo obligaría a calcular el total y validar el cupón en la vista o en el serializer, exactamente lo que la rúbrica prohíbe.

### Por qué Builder (y no, por ejemplo, un serializer más complejo)

Un serializer valida **forma** (tipos, formatos). Un Builder valida **invariantes de construcción** (¿existe al menos un ítem? ¿el cupón sigue vigente? ¿la cantidad es positiva?) y produce un objeto que **no puede existir en un estado inválido** — si `build()` no lanza, el resultado es usable. Esa garantía es justamente lo que un Service necesita antes de tocar la base de datos.

### Implementación

```python
built = (
    OrderBuilder()
    .for_customer(customer)
    .add_item(product, LicenseType.RETAIL, quantity=2)
    .with_coupon(coupon)             # valida vigencia aquí, no al final
    .with_delivery_channel("EMAIL")
    .build()                          # valida invariantes globales, calcula el total
)
```

`build()` devuelve un `BuiltOrder` — un `dataclass` inmutable, no un `Order` de Django. Separar "construir la forma válida del pedido" de "persistirlo" (que hace `OrderService.create_order`) es lo que permite testear todas las reglas del Builder sin tocar la base de datos (ver `sales/tests/test_builders.py`, 8 tests, cero queries).

### Extensión futura

Agregar un nuevo tipo de descuento (ej. descuento por volumen) significa agregar un método `with_volume_discount(...)` al Builder — `OrderService` no cambia.

---

## Factory — `notifications/factories.py::NotificationFactory`

### Problema

Un pedido puede notificarse por Email, SMS o WhatsApp, según la preferencia del cliente. Sin una Factory, `OrderService` (o peor, la vista) terminaría con un `if channel == "EMAIL": ... elif channel == "SMS": ...` — acoplando el caso de uso de checkout a *todos* los proveedores de notificación posibles, y violando Open/Closed (agregar un canal nuevo obligaría a modificar ese `if`).

### Por qué Factory

`NotificationFactory.create(channel)` centraliza la única decisión que varía ("¿qué implementación uso?") detrás de una interfaz común (`Notifier`, con un solo método `send()`). `NotificationService` — y, transitivamente, `OrderService` — dependen únicamente de la abstracción `Notifier`, nunca de `EmailNotifier`/`SMSNotifier`/`WhatsAppNotifier` directamente. Esto es Dependency Inversion aplicado, no solo "un patrón de creación".

### Implementación

```python
class NotificationFactory:
    _REGISTRY = {
        NotificationChannel.EMAIL: EmailNotifier,
        NotificationChannel.SMS: SMSNotifier,
        NotificationChannel.WHATSAPP: WhatsAppNotifier,
    }

    @classmethod
    def create(cls, channel: str) -> Notifier:
        notifier_cls = cls._REGISTRY.get(channel)
        if notifier_cls is None:
            raise UnsupportedNotificationChannelError(...)
        return notifier_cls()
```

### Por qué este caso, y no pasarelas de pago

El PDF ofrece tres ejemplos válidos (notificaciones, pasarelas de pago, generadores de reportes). Se eligió notificaciones porque el proyecto ya tenía una razón de negocio real y verificable para necesitar múltiples canales intercambiables (ver [Domain-Model](Domain-Model.md) y el contexto en el README) — no se inventó el caso de uso para tener una excusa de implementar el patrón.

### Extensión futura

Agregar un canal de "push notification" es: (1) crear `PushNotifier(Notifier)`, (2) agregarlo al `_REGISTRY`. `NotificationService` y `OrderService` no cambian — es la prueba concreta de la pregunta de arquitectura "si mañana cambiamos Email por SMS, ¿hay que tocar el flujo de negocio?" (respuesta: no).

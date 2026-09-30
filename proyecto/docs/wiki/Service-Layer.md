# Service Layer

## Por qué existe

El PDF de la entrega es explícito: **prohibida lógica de negocio en Views o Serializers**, y cada flujo principal debe estar orquestado por una clase en `services.py`. Esto no es solo para cumplir la rúbrica — es lo que permite que:

- Las Views sean triviales de leer (reciben, validan formato, llaman un service, responden).
- Las reglas de negocio se puedan testear sin pasar por HTTP (ver [Testing](Testing.md)).
- Cambiar *cómo* se cumple una regla (ej. de dónde se saca una clave disponible) no obligue a tocar la capa de presentación.

## Servicios existentes

| Servicio | App | Caso de uso que orquesta |
|---|---|---|
| `OrderService` | sales | Checkout completo: construir el pedido (Builder), persistirlo, asignar inventario, notificar. También lecturas (`get_order`, `list_orders_for_customer`) |
| `LicenseAllocationService` | sales | Reservar suficientes `LicenseKey` AVAILABLE para cada línea del pedido, o fallar |
| `PaymentService` | sales | Procesar el pago (simulado) de un pedido, con la regla de "un pago por pedido" |
| `ActivationService` | licensing | Activar una clave en un dispositivo, respetando `activation_limit` |
| `NotificationService` | notifications | Elegir (vía Factory) y usar un `Notifier`, y dejar registro en `Notification` |

Cada uno tiene **una sola razón para cambiar** (SRP): `LicenseAllocationService` solo sabe de disponibilidad de inventario; `PaymentService` solo sabe de la regla de un pago por pedido; ninguno sabe cómo se ve un HTTP request.

## Dónde termina el modelo y empieza el servicio

Regla aplicada consistentemente en todo el proyecto:

> Si una regla se puede decidir mirando **solo las columnas de la propia fila**, puede vivir como método/property del modelo (ej. `Coupon.is_valid_now()`, `OrderItem.subtotal`). Si la regla necesita **consultar otras filas u otras tablas** (¿hay suficiente stock? ¿cuántas activaciones ya existen para esta clave?), vive en un servicio.

Esto es lo que evita tanto "Fat Models" (lógica de negocio real escondida en el modelo) como "servicios anémicos" que solo envuelven `Model.objects.create()` sin agregar nada (ver el ejemplo "mal" abajo).

### Ejemplo de lo que NO se hizo

```python
# Anti-patrón evitado deliberadamente: un "service" que no orquesta nada.
class UserService:
    def create_user(self, data):
        return User.objects.create(**data)
```

`catalog/views.py` y `licensing/views.py` (para el CRUD simple de `SoftwareProduct` y la carga de `LicenseKey`) llaman directamente al serializer sin un service intermedio — precisamente porque no hay ninguna regla de negocio ahí, solo persistencia. Envolverlos en un service habría sido la ceremonia que el ejemplo de arriba ilustra.

### Ejemplo de lo que sí se hizo (`LicenseAllocationService`)

```python
class LicenseAllocationService:
    def reserve_for_order(self, order):
        for item in order.items.select_related("product"):
            available = list(LicenseKey.objects.select_for_update().filter(
                product=item.product, license_type=item.license_type,
                status=LicenseKeyStatus.AVAILABLE,
            )[: item.quantity])
            if len(available) < item.quantity:
                raise InsufficientLicenseStockError(...)
            for key in available:
                key.status = LicenseKeyStatus.SOLD
                key.assigned_order_item = item
                key.save(update_fields=["status", "assigned_order_item"])
```

Esto **no** se puede expresar como método de `Order` o de `LicenseKey` sin que ese modelo empiece a conocer y consultar otras tablas — que es exactamente la definición de "Fat Model" que la rúbrica penaliza.

## Excepciones de dominio, no códigos HTTP

Los servicios nunca devuelven ni deciden un código HTTP — levantan excepciones de `common/exceptions.py` (`EntityNotFoundError`, `InsufficientLicenseStockError`, `PaymentConflictError`, `ActivationLimitExceededError`, etc.). La traducción a 404/409/400 ocurre en un único lugar: `common/drf_exception_handler.py`, registrado en `settings.REST_FRAMEWORK['EXCEPTION_HANDLER']`. Esto significa que **ninguna vista tiene un `try/except`** — las excepciones se propagan y DRF las intercepta automáticamente antes de construir la respuesta.

## Dependency Injection

`OrderService` recibe `NotificationService` y `LicenseAllocationService` por constructor (con defaults a las implementaciones reales). `NotificationService` recibe la clase `NotificationFactory` por constructor. Esto es lo que permite, por ejemplo, testear `NotificationService` con un `Notifier` falso sin tocar ningún proveedor real — ver `notifications/tests/test_services.py::test_notify_uses_injected_factory_instead_of_real_provider`.

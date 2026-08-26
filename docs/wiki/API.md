# API

Todos los endpoints están montados bajo `/api/`. Todos usan `APIView` (no `ViewSet`/`ModelViewSet`), por requisito explícito del PDF.

Todas las respuestas de error de dominio tienen la forma `{"error": "<mensaje>"}` (ver `common/drf_exception_handler.py`); los errores de validación de serializer usan el formato estándar de DRF (`{"campo": ["mensaje"]}`).

## Catálogo

### `GET /api/products/`
Lista productos activos. → **200**

### `POST /api/products/`
```json
{"sku": "WIN11PRO", "name": "Windows 11 Pro", "category": "OS", "base_price": "120.00"}
```
→ **201** con el producto creado · **400** si falta un campo o `base_price <= 0`.

## Licenciamiento

### `GET /api/license-keys/?product=<id>`
Lista claves de licencia (opcionalmente filtradas por producto). → **200**

### `POST /api/license-keys/`
```json
{"product": 1, "license_type": "RETAIL", "key_code": "ABCD-1234", "activation_limit": 1}
```
→ **201** · **400** si `key_code` ya existe o falta un campo.

### `POST /api/license-keys/<id>/activate/`
```json
{"device_fingerprint": "device-hash-123"}
```
→ **200** con el `ActivationRecord` creado
→ **400** si falta `device_fingerprint`
→ **404** si la clave no existe
→ **409** si la clave no está `SOLD`, o si ya alcanzó su `activation_limit`

## Ventas

### `POST /api/customers/`
```json
{"full_name": "Nico Test", "email": "nico@test.com"}
```
→ **201** · **400** si el email ya existe o el formato es inválido.

### `GET /api/customers/<id>/orders/`
Historial de pedidos de un cliente. → **200** · **404** si el cliente no existe.

### `POST /api/coupons/`
```json
{"code": "SAVE10", "percentage_off": "10", "valid_until": "2027-01-01T00:00:00Z"}
```
→ **201** · **400** si `percentage_off` está fuera de 1–100.

### `POST /api/orders/` — flujo principal (checkout)
```json
{
  "customer_id": 1,
  "items": [
    {"product_id": 1, "license_type": "RETAIL", "quantity": 2}
  ],
  "coupon_code": "SAVE10",
  "delivery_channel": "EMAIL"
}
```
→ **201** con el pedido creado (incluye `items` con `subtotal` calculado)
→ **400** si `items` está vacío, una `quantity <= 0`, o el cupón está vencido/inactivo
→ **404** si el cliente, un producto o el cupón no existen
→ **409** si no hay suficientes `LicenseKey` `AVAILABLE` para alguna línea

Internamente dispara, en orden: `OrderBuilder` (valida y calcula el total) → persistencia de `Order`/`OrderItem` → `LicenseAllocationService` (reserva claves) → `NotificationService` (notifica al cliente). Ver [Sequence-Diagram](Sequence-Diagram.md).

### `GET /api/orders/<id>/`
→ **200** con el detalle del pedido · **404** si no existe.

### `POST /api/orders/<id>/pay/`
```json
{"method": "CARD"}
```
→ **200** con el `Payment` creado, y el pedido pasa a `PAID`
→ **400** si `method` no es válido
→ **404** si el pedido no existe
→ **409** si el pedido ya tiene un pago, o no está en estado `PENDING`

## Verificación manual (ejecutada durante el desarrollo)

Los ejemplos de arriba fueron probados en vivo contra `python manage.py runserver` con `curl`, no solo con el test client de Django — incluyendo los casos 400/404/409. El detalle de la corrida está en el reporte de auditoría final de la entrega.

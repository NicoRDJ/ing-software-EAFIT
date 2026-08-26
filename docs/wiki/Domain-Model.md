# Domain Model

## Alcance para esta entrega

El dominio completo de un marketplace de licencias de software (inspirado en el negocio real MyLegitKeys) es más grande que lo que el objetivo de esta entrega pide implementar. Siguiendo el requisito explícito de "50–60% de las clases propuestas", se definieron **16 clases de dominio** en total y se implementaron **9** (56.25%) — las que permiten demostrar el flujo transaccional completo (checkout → asignación de inventario → pago → activación) con reglas de negocio reales, en vez de elegir 9 entidades CRUD triviales solo para llegar al número.

`16 clases propuestas · 9 implementadas · 56.25%`

## Implementadas (9)

| Clase | App | Rol |
|---|---|---|
| `SoftwareProduct` | catalog | Producto vendible (definición, no inventario) |
| `LicenseKey` | licensing | Una clave real y vendible — el inventario de facto |
| `ActivationRecord` | licensing | Un intento de activación de una clave en un dispositivo |
| `Customer` | sales | Comprador |
| `Coupon` | sales | Descuento porcentual con vigencia |
| `Order` | sales | **Agregado raíz** — pedido, siempre construido vía `OrderBuilder` |
| `OrderItem` | sales | Línea de un pedido (producto + tipo de licencia + cantidad) |
| `Payment` | sales | Pago (simulado) asociado 1:1 a un pedido |
| `Notification` | notifications | Registro de un mensaje enviado (o intentado) a un cliente |

## Propuestas, no implementadas en esta entrega (7)

Documentadas aquí para dejar explícito qué falta y por qué no se priorizó ahora — no por accidente:

| Clase | Rol previsto | Por qué se dejó para una entrega futura |
|---|---|---|
| `ProductCategory` (como entidad, no choices) | Categoría de producto con metadata propia (impuestos, reglas por región) | Hoy es un `TextChoices` embebido en `SoftwareProduct`; convertirla en entidad solo se justifica si aparecen reglas por categoría |
| `Review` | Reseña de un cliente sobre un pedido/producto | Requiere moderación y ponderación — fuera del núcleo transaccional evaluado |
| `RefundRequest` | Solicitud de reembolso/reemplazo con flujo de aprobación | Buen candidato para demostrar más transiciones de estado (y más 409) en una entrega futura |
| `Supplier` | Proveedor del que se abastecen las claves | Pertenece al contexto de abastecimiento, no al de ventas expuesto por esta API |
| `KeyProcurementBatch` | Lote de compra de claves a un proveedor | Depende de `Supplier` |
| `SupportTicket` | Caso de soporte asociado a un pedido | Contexto de soporte, no de ventas |
| `SalesReport` | Reporte agregado de ventas/inventario | Candidato natural para una segunda variante de Factory (generadores de reportes) en una entrega futura |

## Relaciones clave

```
SoftwareProduct 1---N LicenseKey
LicenseKey 1---N ActivationRecord
Customer 1---N Order
Order 1---N OrderItem
Order 1---1 Payment
Order 1---N Notification
Order N---1 Coupon (opcional)
OrderItem N---1 SoftwareProduct
LicenseKey N---1 OrderItem (asignación, opcional hasta que se vende)
```

## Validaciones de negocio en el nivel de modelo

- `SoftwareProduct.base_price` — `MinValueValidator(0.01)`: no puede existir un producto gratis o con precio negativo.
- `Coupon.percentage_off` — `MinValueValidator(1)` / `MaxValueValidator(100)`: un descuento fuera de ese rango no tiene sentido de negocio.
- `OrderItem.quantity` — `MinValueValidator(1)`: no existen líneas de pedido con cantidad cero o negativa.
- `Coupon.is_valid_now()` — predicado puro sobre las propias columnas de la fila (no consulta otras tablas); ver la nota de límite en [Service-Layer](Service-Layer.md) sobre por qué esto sigue siendo aceptable en el modelo y no una violación de "Fat Model".

Las reglas que **sí** requieren mirar otras filas/tablas (stock disponible, límite de activaciones) están deliberadamente en la capa de servicios — ver [Service-Layer](Service-Layer.md).

# Sequence Diagram — Checkout (`POST /api/orders/`)

Este es el flujo más complejo del sistema: es el único que atraviesa Serializer → Service → Builder → otro Service → Factory → persistencia → notificación, con dos puntos de falla de negocio distintos (stock insuficiente, cupón inválido) además de la validación de forma del serializer.

```mermaid
sequenceDiagram
    actor Client
    participant View as OrderCreateView
    participant InSer as OrderCreateSerializer
    participant OrderSvc as OrderService
    participant Builder as OrderBuilder
    participant AllocSvc as LicenseAllocationService
    participant NotifSvc as NotificationService
    participant Factory as NotificationFactory
    participant Notifier as Notifier (Email/SMS/WhatsApp)
    participant DB as Django ORM

    Client->>View: POST /api/orders/ {customer_id, items[], coupon_code, delivery_channel}
    View->>InSer: is_valid(raise_exception=True)
    InSer-->>View: validated_data (o 400 si la forma es inválida)

    View->>OrderSvc: create_order(**validated_data)
    activate OrderSvc

    OrderSvc->>DB: Customer.objects.get(pk=customer_id)
    DB-->>OrderSvc: Customer (o EntityNotFoundError -> 404)

    OrderSvc->>Builder: for_customer(customer)
    loop por cada item
        OrderSvc->>DB: SoftwareProduct.objects.get(pk=product_id, is_active=True)
        DB-->>OrderSvc: SoftwareProduct (o EntityNotFoundError -> 404)
        OrderSvc->>Builder: add_item(product, license_type, quantity)
    end
    OrderSvc->>DB: Coupon.objects.get(code=coupon_code)  (si se envió)
    DB-->>OrderSvc: Coupon (o EntityNotFoundError -> 404)
    OrderSvc->>Builder: with_coupon(coupon)
    Builder-->>OrderSvc: InvalidOrderError si el cupón está vencido/inactivo (-> 400)

    OrderSvc->>Builder: build()
    Builder-->>OrderSvc: BuiltOrder (total calculado, invariantes validadas)

    OrderSvc->>DB: Order.objects.create(...)
    OrderSvc->>DB: OrderItem.objects.bulk_create(...)

    OrderSvc->>AllocSvc: reserve_for_order(order)
    activate AllocSvc
    AllocSvc->>DB: LicenseKey.objects.filter(product, license_type, status=AVAILABLE)
    DB-->>AllocSvc: claves disponibles
    alt stock insuficiente
        AllocSvc-->>OrderSvc: InsufficientLicenseStockError
        Note over OrderSvc,DB: @transaction.atomic revierte Order + OrderItems creados
    else stock suficiente
        AllocSvc->>DB: LicenseKey.save(status=SOLD, assigned_order_item)
        AllocSvc-->>OrderSvc: OK
    end
    deactivate AllocSvc

    OrderSvc->>NotifSvc: notify(order, channel, ORDER_CONFIRMATION, ...)
    activate NotifSvc
    NotifSvc->>Factory: create(channel)
    Factory-->>NotifSvc: Notifier concreto (Email/SMS/WhatsApp)
    NotifSvc->>Notifier: send(recipient, message)
    Notifier-->>NotifSvc: True/False
    NotifSvc->>DB: Notification.objects.create(was_sent=...)
    deactivate NotifSvc

    OrderSvc-->>View: Order
    deactivate OrderSvc
    View-->>Client: 201 Created + OrderOutputSerializer(order).data
```

## Puntos a resaltar en la sustentación

1. **La vista nunca decide un status code manualmente** salvo el 201 del camino feliz — todos los errores (400/404/409) llegan como excepciones de dominio y se traducen en `common/drf_exception_handler.py`, fuera de este flujo.
2. **El rollback es real, no solo teórico**: `OrderService.create_order` está decorado con `@transaction.atomic`, así que si `LicenseAllocationService` falla *después* de haber creado `Order`/`OrderItem`, esas filas se revierten — verificado en `sales/tests/test_services.py::test_create_order_with_insufficient_stock_raises_and_rolls_back`.
3. **El Builder se usa antes de tocar la base de datos** — `build()` puede fallar (cupón inválido, sin ítems, sin cliente) sin haber escrito nada.
4. **La Factory aparece recién al final**, y solo detrás de la abstracción `Notifier` — `OrderService` nunca sabe qué canal concreto se usó.

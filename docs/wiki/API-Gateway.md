# API Gateway — Visión de Escalabilidad

**Aclaración importante:** no existe ningún API Gateway desplegado ni configurado en este proyecto. Esta página explica *por qué el desacoplamiento actual haría esa evolución viable el día que se necesite*, no describe infraestructura ya construida.

## Dónde encajaría

```
Client
   |
API Gateway            <- autenticación, rate limiting, TLS termination, logging, routing, versionado
   |
Django API (este proyecto, sin cambios en su lógica interna)
   |
Application Services (OrderService, PaymentService, ActivationService, NotificationService...)
   |
Domain (models + Builder + Factory)
```

## Por qué el diseño actual ya está preparado para esto

1. **Las URLs ya están versionables por app.** `config/urls.py` monta cada app bajo `/api/` a través de sus propios `urls.py`. Introducir un prefijo de versión (`/api/v1/...`) o mover una app entera detrás de una ruta distinta del Gateway no toca ni un service ni un modelo — es un cambio de `include()`.

2. **Los servicios no saben nada de HTTP.** `OrderService`, `PaymentService`, `ActivationService` reciben tipos de Python (ints, dicts, strings) y devuelven instancias de modelo — nunca un `Request` ni un `Response`. Si mañana el Gateway decide invocar estos casos de uso por gRPC o por un worker asíncrono en vez de HTTP directo, la capa de presentación (`views.py`) es lo único que cambiaría.

3. **La autenticación/autorización no está mezclada con las reglas de negocio.** Hoy no hay autenticación implementada (fuera de alcance de esta entrega); cuando se agregue, el lugar natural es un `authentication_classes`/`permission_classes` en las Views o, más adelante, delegarla por completo al Gateway (JWT validado aguas arriba, el backend confía en un header ya verificado) — en ningún caso los `services.py` necesitan saber quién es el usuario más allá de los IDs que ya reciben como parámetros.

4. **El exception handler centralizado (`common/drf_exception_handler.py`) es, en efecto, un contrato de errores único.** Un Gateway que necesite mapear errores de negocio a un formato estándar (RFC 7807, por ejemplo) solo tiene un punto de traducción que ajustar, no N vistas.

5. **Cada app es un candidato natural a servicio independiente si el sistema creciera.** `licensing` (inventario de claves + activaciones) y `sales` (checkout + pagos) tienen escalas de carga y de riesgo muy distintas — un pico de tráfico de activaciones no debería poder tumbar el checkout. La separación por app hoy (con dependencias explícitas y mínimas entre ellas, ver [Architecture](Architecture.md)) es lo que haría viable, en el futuro, separar `licensing` en su propio servicio detrás del mismo Gateway sin reescribir su lógica interna.

## Qué NO se afirma

No se afirma que el sistema ya sea "microservicios-ready" ni que deba serlo pronto — para el volumen de este proyecto, un monolito modular es la elección correcta (ver el principio de "no sobreingeniería" aplicado en todo el proyecto). Lo que se afirma es que el desacoplamiento Service Layer / Domain / Presentación no es una casualidad: es lo que hace que esa evolución, si algún día es necesaria, sea un cambio de infraestructura y no una reescritura.

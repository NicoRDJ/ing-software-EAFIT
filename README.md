# Ingeniería de Software — Arquitectura de Software 2026

**Entrega No. 1: Núcleo de Negocio y Exposición de API Profesional**

## Contexto del dominio

El sistema modela un **marketplace de licencias de software** (venta de claves de activación de Windows, Office y productos similares, con distintos tipos de licencia — Retail, OEM, MAK, Volumen). El dominio está inspirado en un negocio real que opero (**MyLegitKeys**, una plataforma de reventa de licencias de software), pero **para efectos de esta entrega el alcance fue reenfocado deliberadamente** al núcleo transaccional que el curso evalúa — checkout, asignación de inventario de licencias, pago y activación — dejando fuera de alcance el resto de la plataforma comercial real (marketing, soporte, abastecimiento, etc.), que no aporta al objetivo de la entrega.

Una decisión de diseño concreta viene directamente de la operación real del negocio: el soporte de múltiples canales de notificación (Email, SMS, WhatsApp) no es un capricho académico — nace de un hallazgo real de una auditoría operativa de MyLegitKeys, donde un cliente reportó no poder ser contactado ni por email ni por WhatsApp tras un problema. Modelar el canal como una dependencia intercambiable (ver `notifications/factories.py`) es la respuesta arquitectónica a ese problema real.

## Arquitectura

```
config/            Proyecto Django (settings, urls raíz, wsgi/asgi)
common/            Excepciones de dominio + exception handler de DRF (sin modelos)
catalog/           SoftwareProduct — catálogo de productos vendibles
licensing/         LicenseKey, ActivationRecord — inventario real y activaciones
sales/             Customer, Order, OrderItem, Coupon, Payment — ventas
notifications/     Notification, Notifier(s), NotificationFactory — envíos
docs/wiki/         Contenido listo para pegar en el Wiki de GitHub
DEFENSE_GUIDE.md   Guía de preparación para la sustentación oral
```

Cada app Django representa un contexto acotado del dominio (catálogo, licenciamiento, ventas, notificaciones). `common/` no tiene modelos — solo excepciones de dominio y el traductor de excepciones a HTTP — por eso no está en `INSTALLED_APPS`. La justificación completa de esta estructura está en [`docs/wiki/Architecture.md`](docs/wiki/Architecture.md).

## Requisitos

- Python 3.11+
- pip

## Instalación y ejecución

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo         # crea producto, licencias, cliente y cupón de ejemplo
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/api/`.

## Correr los tests

```bash
python manage.py test
```

40 tests (unitarios de Builder/Factory/Services + de integración sobre la API) — deberían pasar todos.

Para lint (opcional, requiere `requirements-dev.txt`):

```bash
pip install -r requirements-dev.txt
ruff check .
```

## Endpoints principales

| Método | Endpoint | Descripción | Éxito | Errores |
|---|---|---|---|---|
| GET | `/api/products/` | Listar productos activos | 200 | — |
| POST | `/api/products/` | Crear producto | 201 | 400 |
| GET | `/api/license-keys/?product=<id>` | Listar inventario de claves | 200 | — |
| POST | `/api/license-keys/` | Cargar una clave de licencia | 201 | 400 |
| POST | `/api/license-keys/<id>/activate/` | Activar una clave en un dispositivo | 200 | 400, 404, 409 |
| POST | `/api/customers/` | Registrar cliente | 201 | 400 |
| GET | `/api/customers/<id>/orders/` | Historial de pedidos de un cliente | 200 | 404 |
| POST | `/api/coupons/` | Crear cupón | 201 | 400 |
| **POST** | **`/api/orders/`** | **Checkout — flujo principal (Builder + Service Layer + Factory)** | **201** | **400, 404, 409** |
| GET | `/api/orders/<id>/` | Detalle de un pedido | 200 | 404 |
| POST | `/api/orders/<id>/pay/` | Procesar pago de un pedido | 200 | 400, 404, 409 |

Ver [`docs/wiki/API.md`](docs/wiki/API.md) para el detalle completo de payloads.

## Cómo probar el flujo principal manualmente

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [{"product_id": 1, "license_type": "RETAIL", "quantity": 2}],
    "coupon_code": "EAFIT10",
    "delivery_channel": "EMAIL"
  }'
```

(los IDs de ejemplo son los que imprime `seed_demo`).

## Documentación

- [`docs/wiki/`](docs/wiki/) — contenido completo de la Wiki técnica (arquitectura, dominio, Service Layer, patrones, API, diagrama de secuencia, API Gateway, testing). Ver instrucciones de publicación abajo.

### Publicar la Wiki en GitHub

El Wiki de este repositorio no estaba habilitado al momento de esta entrega. Para publicarlo:

1. En GitHub → Settings → Features → marcar **Wikis**.
2. Abrir la pestaña **Wiki** del repo y crear la página `Home` (cualquier contenido, luego se reemplaza).
3. Clonar `git@github.com:NicoRDJ/ing-software-EAFIT.wiki.git` y copiar cada archivo de `docs/wiki/*.md` como una página (mismo nombre sin `.md`), o pegar el contenido manualmente desde la interfaz web.

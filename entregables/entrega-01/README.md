# Entrega 1 — Núcleo de Negocio y Exposición de API Profesional

**Fecha de entrega:** 2026-08-26 · **Tag:** [`entrega-01`](https://github.com/NicoRDJ/ing-software-EAFIT/tree/entrega-01) (estado exacto del código entregado)

## Qué se pidió y dónde está

| Requisito | Implementación |
|---|---|
| Modelo de dominio del negocio | `proyecto/catalog`, `proyecto/licensing`, `proyecto/sales`, `proyecto/notifications` — Wiki: *Domain-Model* |
| Lógica de negocio fuera de vistas y serializers (Service Layer) | `*/services.py` — Wiki: *Service-Layer* |
| Patrón Builder | `proyecto/sales/builders.py` (`OrderBuilder`) |
| Patrón Factory (dependencia variable) | `proyecto/notifications/factories.py` (`NotificationFactory`) |
| API REST profesional con DRF | `*/views.py`, `*/serializers.py` — Wiki: *API* |
| Manejo centralizado de errores | `proyecto/common/drf_exception_handler.py` |
| Pruebas | `*/tests/` (40 tests) — Wiki: *Testing* |
| Documentación técnica | [Wiki](https://github.com/NicoRDJ/ing-software-EAFIT/wiki) |

> Al reorganizar el repositorio de la materia, el código pasó de la raíz a `proyecto/`. El *tag* conserva la estructura original tal como se entregó.

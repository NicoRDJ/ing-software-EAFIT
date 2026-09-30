# Home

## Qué es este proyecto

Backend de un marketplace de licencias de software (Windows, Office, y productos similares), construido con Django + Django REST Framework para el curso **Arquitectura de Software 2026** (Prof. Nicolás Ramírez Vélez), Entrega No. 1.

El dominio está inspirado en un negocio real que opera el autor (**MyLegitKeys**), reenfocado para esta entrega al núcleo transaccional que el curso evalúa: catálogo, checkout, asignación de inventario de licencias, pago y activación. Ver [Domain-Model](Domain-Model.md) para el detalle de qué se dejó dentro y fuera de alcance, y por qué.

## Estado de la Entrega 1

| Requisito | Estado |
|---|---|
| 50–60% de las clases de dominio propuestas | ✅ 9/16 (56.25%) — ver [Domain-Model](Domain-Model.md) |
| Service Layer, sin lógica de negocio en Views/Serializers | ✅ — ver [Service-Layer](Service-Layer.md) |
| DRF: Serializers + APIView + códigos HTTP correctos | ✅ — ver [API](API.md) |
| Builder para la entidad más compleja | ✅ `OrderBuilder` — ver [Design-Patterns](Design-Patterns.md) |
| Factory para una dependencia externa/variante | ✅ `NotificationFactory` — ver [Design-Patterns](Design-Patterns.md) |
| Diagrama de secuencia del flujo más complejo | ✅ — ver [Sequence-Diagram](Sequence-Diagram.md) |
| Explicación de preparación para API Gateway | ✅ — ver [API-Gateway](API-Gateway.md) |

## Taller 02 — Strangler Pattern

Primer módulo extraído del monolito: **Notificaciones** pasa a un microservicio Flask detrás de Nginx. Matriz de decisión, arquitectura, separación técnica y evidencia en [Migración a Microservicios (Strangler Pattern)](Migración-a-Microservicios-(Strangler-Pattern)).

## Arquitectura general

Cuatro apps Django por contexto acotado (`catalog`, `licensing`, `sales`, `notifications`) más un paquete `common/` sin modelos para excepciones de dominio y su traducción a HTTP. El detalle completo, con la justificación de por qué se organizó así, está en [Architecture](Architecture.md).

## Índice

- [Migración a Microservicios (Strangler Pattern)](Migración-a-Microservicios-(Strangler-Pattern)) — Taller 02: módulo de notificaciones en Flask
- [Architecture](Architecture.md) — estructura de carpetas y su justificación
- [Domain-Model](Domain-Model.md) — entidades implementadas vs. propuestas
- [Service-Layer](Service-Layer.md) — cómo y por qué existe esta capa
- [Design-Patterns](Design-Patterns.md) — Builder y Factory
- [API](API.md) — endpoints, payloads, códigos de estado
- [Sequence-Diagram](Sequence-Diagram.md) — flujo de checkout paso a paso
- [API-Gateway](API-Gateway.md) — visión de escalabilidad
- [Testing](Testing.md) — estrategia y cómo correr los tests

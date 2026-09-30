# Taller 02 — El Patrón Estrangulador

**Migración híbrida de monolito a microservicios** · Prof. Nicolás Ramírez Vélez · Arquitectura de Software 2026

Módulo estrangulado: **Notificaciones** (Email / SMS / WhatsApp). Pasa del monolito Django a un microservicio Flask, con Nginx como fachada y Docker Compose como orquestador.

📄 **Documentación completa (matriz de decisión, diagrama, impacto y evidencia):** [Wiki → Migración a Microservicios (Strangler Pattern)](https://github.com/NicoRDJ/ing-software-EAFIT/wiki/Migraci%C3%B3n-a-Microservicios-(Strangler-Pattern))

## Rúbrica → dónde está cada cosa

| Componente | Evidencia |
|---|---|
| Matriz de decisión (≥ 3 módulos) | Wiki, sección 1: evalúa 4 módulos (Catálogo, Licenciamiento, Ventas, Notificaciones) |
| Microservicio Flask (JSON nativo, errores 400/500) | [`proyecto/servicios/notificaciones/`](../../proyecto/servicios/notificaciones/) · 10 pruebas en `tests/` |
| Infraestructura y ruteo | [`proyecto/docker-compose.yml`](../../proyecto/docker-compose.yml) · [`proyecto/nginx/nginx.conf`](../../proyecto/nginx/nginx.conf) |
| Wiki del repo | Explica el impacto esperado e incluye diagramas Mermaid (flujo y secuencia) |
| Git Flow | Rama `feature/taller-02-strangler` con commits semánticos, integrada por Pull Request |

## Ejecutar

```bash
cd proyecto
docker compose up -d --build
curl http://localhost/api/v1/products/                 # monolito Django (v1)
curl -X POST http://localhost/api/v2/notificaciones \
     -H "Content-Type: application/json" \
     -d '{"channel": "EMAIL", "recipient": "cliente@correo.com", "message": "Tu licencia"}'   # Flask (v2)
```

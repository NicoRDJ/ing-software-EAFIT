# Tutoriales del curso

Ejercicios guiados sobre la **Tienda** de ejemplo del profesor (proyecto base `TEIS-DjangoSOLID`). Viven en [`tienda/`](tienda/) y son **independientes del proyecto final**: no comparten código ni base de datos con `proyecto/`.

Cada tutorial es un commit del historial de `tienda/`, así que el estado exacto de cada entrega se puede consultar en ese commit.

| # | Tema | Commit | Qué se entregó | Informe |
|---|---|---|---|---|
| 01 | Evolución de arquitectura en Django (FBV → CBV → Service Layer) | `1a1310e` | Resumen de código + log de pagos | (entregado en clase) |
| 02 | Patrones creacionales: Factory Method y Builder | `79dda70` | Captura consola Mock + `factories.py` / `builders.py` + reflexión | [PDF](entregas/Tutorial_Factory_Builder_NicolasRodriguez.pdf) |
| 03 | API REST con DRF reutilizando el Service Layer | `e7599fe` | Log de pagos + captura POST `/api/v1/comprar/` | [PDF](entregas/Tutorial_DRF_API_NicolasRodriguez.pdf) |
| 04 | Dockerización (PostgreSQL) y despliegue en AWS EC2 | `82457b5` | Captura de la API servida desde EC2 `:8000` | [PDF](entregas/Tutorial_Docker_AWS_NicolasRodriguez.pdf) |
| 05 | Nginx + Gunicorn: el escudo arquitectónico | `e11d97d` | Enrutamiento por :80, aislamiento de :8000, `docker ps` en EC2 | [PDF](entregas/Tutorial_Nginx_Strangler_NicolasRodriguez.pdf) |
| 06 | Primer estrangulamiento: compras v2 en Flask | `cab5e2d` | Postman v1/v2 + logs de Nginx (PDF) | [PDF](entregas/Tutorial_Flask_Microservicio_NicolasRodriguez.pdf) |

Los informes en PDF (con las capturas de evidencia, incluidas las del despliegue en AWS EC2) están en [`entregas/`](entregas/).

Cómo correr la Tienda: ver [`tienda/README.md`](tienda/README.md).

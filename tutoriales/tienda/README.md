# Tienda — Tutoriales Arquitectura de Software 2026 (Nicolás Rodríguez)

Proyecto base del curso (TEIS-DjangoSOLID) evolucionado tutorial a tutorial. Cada tutorial es un commit (historial conservado al importarlo a `tutoriales/tienda/`). Todos los comandos se corren dentro de esta carpeta.

| Tutorial | Qué agrega |
|---|---|
| 01 | Compra Rápida: CBV + Service Layer, log de pagos |
| 02 | `PaymentFactory` (Factory Method por variable de entorno) y `OrdenBuilder` |
| 03 | API REST con DRF: `POST /api/v1/comprar/` reutilizando el Service Layer |
| 04 | Settings por variables de entorno, `Dockerfile`, `docker-compose.yml` con PostgreSQL |
| 05 | Gunicorn + Nginx como proxy inverso (Django aislado) |
| 06 | Microservicio Flask `POST /api/v2/comprar` y ruteo Strangler en Nginx |

## Correr en local (sin Docker)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate && python manage.py seed_tienda
PAYMENT_PROVIDER=MOCK python manage.py runserver   # o sin la variable para usar el banco
python manage.py test tienda_app
```
Usuario demo: `nicolas` / `tienda2026`.

## Correr con Docker
```bash
docker compose up -d --build
# http://localhost/api/v1/productos/   -> Django (v1)
# http://localhost/api/v2/comprar      -> Flask (v2, POST)
```

## Desplegar en AWS EC2 (Amazon Linux 2023)
```bash
curl -fsSL https://raw.githubusercontent.com/NicoRDJ/ing-software-EAFIT/main/tutoriales/tienda/deploy/ec2_setup.sh | bash
```
Security Group: abrir HTTP (80).

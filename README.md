# Ingeniería de Software — Arquitectura de Software 2026 · Universidad EAFIT

Repositorio de la materia de **Nicolás Rodríguez**. Todo el trabajo del semestre vive aquí, separado por tipo para que el proyecto final no se mezcle con los ejercicios de clase.

| Sección | Qué contiene |
|---|---|
| [`proyecto/`](proyecto/) | **Proyecto final** — Marketplace de licencias de software (Django + DRF). Es el sistema que evoluciona con cada entrega y cada taller. |
| [`entregables/`](entregables/) | Una página por entrega del proyecto, con lo que se pidió, dónde está en el código y el *tag* de git que la congela. |
| [`talleres/`](talleres/) | Talleres en clase aplicados **sobre el proyecto final** (enunciado resuelto + enlaces al código y a la Wiki). |
| [`tutoriales/`](tutoriales/) | Tutoriales guiados del curso sobre la *Tienda* de ejemplo del profesor. Proyecto independiente: no comparte código con `proyecto/`. |

La documentación técnica del proyecto está en la **[Wiki](https://github.com/NicoRDJ/ing-software-EAFIT/wiki)** (fuente también en [`proyecto/docs/wiki/`](proyecto/docs/wiki/)).

## Índice

### Entregables del proyecto
| Entrega | Tema | Tag |
|---|---|---|
| [Entrega 1](entregables/entrega-01/) | Núcleo de negocio y exposición de API profesional | `entrega-01` |

### Talleres
| Taller | Tema |
|---|---|
| [Taller 02](talleres/taller-02-strangler/) | El Patrón Estrangulador: migración híbrida de monolito a microservicios |

### Tutoriales
Ver [`tutoriales/README.md`](tutoriales/README.md).

## Convenciones
- Commits semánticos (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- Cada entrega queda marcada con un *tag* (`entrega-NN`); cada taller se integra por *Pull Request* desde una rama `feature/taller-NN-*`.

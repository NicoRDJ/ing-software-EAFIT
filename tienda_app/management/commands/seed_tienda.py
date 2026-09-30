from django.core.management.base import BaseCommand

from tienda_app.models import Inventario, Libro

LIBROS = [
    ("Cien años de soledad", "150.00", 10),
    ("Clean Architecture", "180.00", 10),
    ("Patrones de Diseño (GoF)", "165.00", 10),
    ("Domain-Driven Design", "210.00", 10),
]


class Command(BaseCommand):
    help = "Carga los libros de demo con su inventario (idempotente)."

    def handle(self, *args, **options):
        for titulo, precio, cantidad in LIBROS:
            libro, creado = Libro.objects.get_or_create(titulo=titulo, defaults={"precio": precio})
            Inventario.objects.get_or_create(libro=libro, defaults={"cantidad": cantidad})
            estado = "creado" if creado else "ya existía"
            self.stdout.write(f"  [{libro.id}] {libro.titulo} ({estado})")
        self.stdout.write(self.style.SUCCESS("Catálogo listo."))

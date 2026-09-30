from decimal import Decimal

from django.shortcuts import get_object_or_404
from .models import Libro, Inventario, Orden
from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos

class CompraService:
    """
    SERVICE LAYER: Orquesta la interacción entre el dominio, 
    la infraestructura y la base de datos.
    """
    def __init__(self, procesador_pago):
        # Inyectamos la dependencia (DIP)
        self.procesador = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_proceso_compra(self, usuario, lista_productos, direccion):
        # Uso del Builder: Semantica clara y validacion interna
        orden = (self.builder
                 .con_usuario(usuario)
                 .con_productos(lista_productos)
                 .para_envio(direccion)
                 .build())

        # Uso del Factory (inyectado): Cambio de comportamiento sin cambio de codigo
        if self.procesador.pagar(orden.total):
            return f"Orden {orden.id} procesada exitosamente."

        orden.delete()
        raise Exception("Error en la pasarela de pagos.")

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        # Regla de negocio: no se vende lo que no hay
        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        orden = (self.builder
                 .con_usuario(usuario)
                 .con_productos([libro] * cantidad)
                 .para_envio(direccion)
                 .build())

        if not self.procesador.pagar(orden.total):
            orden.delete()
            raise Exception("La transacción fue rechazada por el banco.")

        inv.cantidad -= cantidad
        inv.save()
        return orden.total


class CompraRapidaService:
    """
    SERVICE LAYER del flujo "Compra Rápida" (tutorial 01).
    La vista NO sabe nada del negocio: solo pide "procesar" y recibe un total.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def obtener_detalle(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def procesar(self, libro_id, usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        if inv.cantidad <= 0:
            raise ValueError("No hay existencias.")

        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        if not self.procesador_pago.pagar(total):
            raise Exception("La transacción fue rechazada por el banco.")

        inv.cantidad -= 1
        inv.save()
        Orden.objects.create(libro=libro, total=Decimal(str(round(total, 2))))
        return total

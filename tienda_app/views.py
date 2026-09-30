from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .infra.gateways import BancoNacionalProcesador
from .models import Inventario, Orden
from .services import CompraRapidaService, CompraService


class CompraView(View):
    """
    CBV: Vista Basada en Clases.
    Actúa como un "Portero": recibe la petición y delega al servicio.
    """
    template_name = 'tienda_app/compra.html'

    # Configuramos el servicio con su implementación de infraestructura
    def setup_service(self):
        gateway = BancoNacionalProcesador()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(request, self.template_name, {
                'mensaje_exito': f"¡Gracias por su compra! Total: ${total}",
                'total': total
            })
        except (ValueError, Exception) as e:
            # Manejo de errores de negocio transformados a respuesta de usuario
            return render(request, self.template_name, {
                'error': str(e)
            }, status=400)


class CompraRapidaView(View):
    """
    CBV "Skinny View" (tutorial 01). La vista no tiene lógica de negocio:
    GET y POST solo delegan en CompraRapidaService y traducen a HTTP.
    """
    template_name = 'tienda_app/compra_rapida.html'

    def setup_service(self):
        return CompraRapidaService(procesador_pago=BancoNacionalProcesador())

    def get(self, request, libro_id):
        return render(request, self.template_name, self.setup_service().obtener_detalle(libro_id))

    def post(self, request, libro_id):
        try:
            total = self.setup_service().procesar(libro_id)
            return HttpResponse(f"Compra rápida exitosa. Total: ${total:.2f}")
        except (ValueError, Exception) as e:
            return HttpResponse(str(e), status=400)


def inventario_view(request):
    """Vista HTML de solo lectura: stock actual de cada libro."""
    return render(request, 'tienda_app/inventario.html', {
        'inventario': Inventario.objects.select_related('libro').order_by('libro_id'),
        'total_ordenes': Orden.objects.count(),
    })

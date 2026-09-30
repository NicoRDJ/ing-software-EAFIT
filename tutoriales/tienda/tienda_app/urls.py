from django.urls import path
from tienda_app.api.views import CompraAPIView, LibroListAPIView
from .views import CompraView, CompraRapidaView, inventario_view

urlpatterns = [
    path('', inventario_view, name='inventario'),
    # Usamos .as_view() para habilitar la CBV
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),
    path('compra-rapida/<int:libro_id>/', CompraRapidaView.as_view(), name='compra_rapida'),
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
    path('api/v1/productos/', LibroListAPIView.as_view(), name='api_productos'),
]

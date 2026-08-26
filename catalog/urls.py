from django.urls import path

from catalog.views import ProductListCreateView

urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
]

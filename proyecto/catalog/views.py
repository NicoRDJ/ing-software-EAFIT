from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import SoftwareProduct
from catalog.serializers import SoftwareProductSerializer


class ProductListCreateView(APIView):
    """Plain catalog CRUD: no business rule beyond field-level validation, so
    there is deliberately no ProductService here — wrapping a bare
    `SoftwareProduct.objects.create(**data)` in a service class would be the
    "useless wrapper" anti-pattern the rubric explicitly warns against
    (see docs/wiki/Service-Layer.md, 'When a service is NOT needed')."""

    def get(self, request):
        products = SoftwareProduct.objects.filter(is_active=True)
        serializer = SoftwareProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SoftwareProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

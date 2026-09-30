from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from licensing.models import LicenseKey
from licensing.serializers import ActivationInputSerializer, ActivationOutputSerializer, LicenseKeySerializer
from licensing.services import ActivationService


class LicenseKeyListCreateView(APIView):
    """Inventory seeding endpoint (e.g. loading a batch of keys purchased
    from a supplier). Plain persistence, no service — see the same note on
    catalog.views.ProductListCreateView."""

    def get(self, request):
        product_id = request.query_params.get("product")
        keys = LicenseKey.objects.all()
        if product_id:
            keys = keys.filter(product_id=product_id)
        return Response(LicenseKeySerializer(keys, many=True).data)

    def post(self, request):
        serializer = LicenseKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LicenseKeyActivationView(APIView):
    """The showcase endpoint for the licensing context: delegates entirely to
    ActivationService, whose ActivationLimitExceededError / ActivationNotAllowedError
    / EntityNotFoundError are translated to 409 / 409 / 404 by the shared
    exception handler — this view never inspects a status code itself."""

    def post(self, request, key_id):
        input_serializer = ActivationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        record = ActivationService().activate(
            license_key_id=key_id,
            device_fingerprint=input_serializer.validated_data["device_fingerprint"],
        )
        return Response(ActivationOutputSerializer(record).data, status=status.HTTP_200_OK)

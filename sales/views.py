from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from sales.models import Coupon, Customer
from sales.serializers import (
    CouponSerializer,
    CustomerSerializer,
    OrderCreateSerializer,
    OrderOutputSerializer,
    PaymentInputSerializer,
    PaymentOutputSerializer,
)
from sales.services import OrderService, PaymentService


class CustomerListCreateView(APIView):
    def get(self, request):
        return Response(CustomerSerializer(Customer.objects.all(), many=True).data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CouponListCreateView(APIView):
    def get(self, request):
        return Response(CouponSerializer(Coupon.objects.all(), many=True).data)

    def post(self, request):
        serializer = CouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderCreateView(APIView):
    """The showcase flow. Everything past `is_valid` is a single call into
    OrderService — this view has no knowledge of Builder, Factory,
    LicenseAllocationService, or how any HTTP status other than 201 gets
    chosen. See docs/wiki/Sequence-Diagram.md for the full request path."""

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        order = OrderService().create_order(
            customer_id=data["customer_id"],
            items=data["items"],
            coupon_code=data.get("coupon_code") or None,
            delivery_channel=data["delivery_channel"],
            notes=data.get("notes", ""),
        )
        return Response(OrderOutputSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    def get(self, request, order_id):
        order = OrderService().get_order(order_id)
        return Response(OrderOutputSerializer(order).data)


class OrderPaymentView(APIView):
    def post(self, request, order_id):
        input_serializer = PaymentInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        order = OrderService().get_order(order_id)
        payment = PaymentService().process_payment(order=order, **input_serializer.validated_data)
        return Response(PaymentOutputSerializer(payment).data, status=status.HTTP_200_OK)


class CustomerOrderListView(APIView):
    def get(self, request, customer_id):
        orders = OrderService().list_orders_for_customer(customer_id)
        return Response(OrderOutputSerializer(orders, many=True).data)

from django.urls import path

from sales.views import (
    CouponListCreateView,
    CustomerListCreateView,
    CustomerOrderListView,
    OrderCreateView,
    OrderDetailView,
    OrderPaymentView,
)

urlpatterns = [
    path("customers/", CustomerListCreateView.as_view(), name="customer-list-create"),
    path("customers/<int:customer_id>/orders/", CustomerOrderListView.as_view(), name="customer-order-list"),
    path("coupons/", CouponListCreateView.as_view(), name="coupon-list-create"),
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:order_id>/pay/", OrderPaymentView.as_view(), name="order-pay"),
]

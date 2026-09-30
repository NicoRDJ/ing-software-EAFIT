from django.urls import path

from licensing.views import LicenseKeyActivationView, LicenseKeyListCreateView

urlpatterns = [
    path("license-keys/", LicenseKeyListCreateView.as_view(), name="license-key-list-create"),
    path("license-keys/<int:key_id>/activate/", LicenseKeyActivationView.as_view(), name="license-key-activate"),
]

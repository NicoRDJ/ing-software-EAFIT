"""
URL configuration for config project.

Root router: each bounded-context app owns its own urls.py; this file only
mounts them under /api/. See docs/wiki/Architecture.md for the folder
structure rationale.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalog.urls')),
    path('api/', include('sales.urls')),
    path('api/', include('licensing.urls')),
]

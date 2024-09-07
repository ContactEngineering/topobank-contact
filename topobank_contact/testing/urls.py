"""
Making urls from topobank available for tests.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path(
        "files/",
        include("topobank.files.urls", namespace="files"),
    ),
    path(
        "manager/",
        include("topobank.manager.urls", namespace="manager"),
    ),
    path(
        "analysis/",
        include("topobank.analysis.urls", namespace="analysis"),
    ),
    path("accounts/", include("allauth.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

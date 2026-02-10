from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Oppvenuz API",
        default_version="v1",
        description="Oppvenuz backend APIs",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
   

    # ✅ Pinterest APIs
    path("api/pinterest/", include("pinterest.urls")),

]

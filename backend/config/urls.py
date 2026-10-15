from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

def home(request):
    return JsonResponse({"name": "Law Case Management API", "api": "/api/", "admin": "/admin/"})

urlpatterns = [path("", home), path("admin/", admin.site.urls), path("api/", include("cases.urls"))]

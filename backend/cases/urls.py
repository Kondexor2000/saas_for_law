from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import CaseViewSet, csrf_cookie, lawyer_list, session_login, session_logout, session_me

router = DefaultRouter()
router.register("cases", CaseViewSet, basename="case")
urlpatterns = [path("", include(router.urls)), path("lawyers/", lawyer_list, name="lawyer-list"), path("csrf/", csrf_cookie, name="csrf-cookie"),
    path("auth/login/", session_login, name="session-login"), path("auth/me/", session_me, name="session-me"), path("auth/logout/", session_logout, name="session-logout")]

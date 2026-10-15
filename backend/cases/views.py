from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from .models import Case
from .permissions import CasePermission, is_admin, is_lawyer
from .serializers import CaseSerializer


class CaseViewSet(viewsets.ModelViewSet):
    serializer_class = CaseSerializer
    permission_classes = [CasePermission]

    def get_queryset(self):
        user = self.request.user
        if is_admin(user):
            return Case.objects.select_related("client", "lawyer")
        if is_lawyer(user):
            return Case.objects.filter(lawyer=user).select_related("client", "lawyer")
        if user.is_authenticated:
            return Case.objects.filter(client=user).select_related("client", "lawyer")
        return Case.objects.none()

    def perform_create(self, serializer):
        client = self.request.user if self.request.user.is_authenticated else None
        serializer.save(client=client)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if not is_admin(self.request.user):
            child = getattr(serializer, "child", serializer)
            child.fields.pop("lawyer", None)
            child.fields.pop("status", None)
        return serializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lawyer_list(request):
    if not is_admin(request.user):
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Tylko administrator może wyświetlić listę prawników.")
    from django.contrib.auth import get_user_model
    User = get_user_model()
    lawyers = User.objects.filter(groups__name="Lawyer", is_active=True).distinct().order_by("username")
    return Response([{"id": user.id, "username": user.username, "name": user.get_full_name()} for user in lawyers])


@api_view(["GET"])
@permission_classes([])
@ensure_csrf_cookie
def csrf_cookie(request):
    return Response({"detail": "CSRF cookie set"})

@api_view(["POST"])
@permission_classes([])
@csrf_protect
def session_login(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        return Response({"detail": "Nieprawidłowy login lub hasło."}, status=400)
    login(request, user)
    return Response({"id": user.id, "username": user.username, "name": user.get_full_name(),
                     "role": "administrator" if is_admin(user) else "lawyer" if is_lawyer(user) else "client"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_me(request):
    user = request.user
    return Response({"id": user.id, "username": user.username, "name": user.get_full_name(),
                     "role": "administrator" if is_admin(user) else "lawyer" if is_lawyer(user) else "client"})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def session_logout(request):
    logout(request)
    return Response({"detail": "Wylogowano."})

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Case

User = get_user_model()
admin.site.unregister(User)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "client_email", "client_phone", "lawyer", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description", "client_email", "client_phone", "client__username", "lawyer__username")


@admin.register(User)
class LawyerUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "is_staff", "lawyer_group")
    list_filter = ("is_staff", "is_active", "groups__name")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Dane osobowe", {"fields": ("first_name", "last_name", "email")}),
        ("Uprawnienia", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "password1", "password2")}),
    )

    def save_model(self, request, obj, form, change):
        creating_account = not change
        if creating_account:
            obj.is_staff = True
            obj.is_superuser = False
        super().save_model(request, obj, form, change)
        if creating_account:
            lawyer_group, _ = Group.objects.get_or_create(name="Lawyer")
            obj.groups.set([lawyer_group])

    @admin.display(description="Rola")
    def lawyer_group(self, obj):
        if obj.groups.filter(name="Lawyer").exists():
            return "Lawyer"
        if obj.is_staff or obj.is_superuser:
            return "Administrator"
        return "Client"

    @admin.action(description="Przypisz wybranym użytkownikom rolę prawnika")
    def assign_lawyer_role(self, request, queryset):
        lawyer_group, _ = Group.objects.get_or_create(name="Lawyer")
        for user in queryset:
            user.groups.add(lawyer_group)
            user.is_staff = True
            user.save(update_fields=["is_staff"])

    actions = [assign_lawyer_role]

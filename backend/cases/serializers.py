from rest_framework import serializers
from .models import Case

class CaseSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    lawyer_name = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = ["id", "client", "client_name", "client_phone", "client_email", "lawyer", "lawyer_name", "title", "category", "description", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "client", "client_name", "lawyer_name", "status", "created_at", "updated_at"]

    def get_client_name(self, obj):
        if obj.client is None:
            return None
        return obj.client.get_full_name() or obj.client.username

    def get_lawyer_name(self, obj):
        if obj.lawyer is None:
            return None
        return obj.lawyer.get_full_name() or obj.lawyer.username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .permissions import is_admin
        request = self.context.get("request")
        if request and is_admin(request.user):
            self.fields["status"].read_only = False

    def validate_lawyer(self, lawyer):
        from .permissions import is_admin
        request = self.context.get("request")
        if not request or not is_admin(request.user):
            raise serializers.ValidationError("Tylko administrator może przypisywać prawnika.")
        if lawyer is None:
            return lawyer
        if not lawyer.groups.filter(name="Lawyer").exists():
            raise serializers.ValidationError("Wybrane konto nie ma roli prawnika.")
        return lawyer

    def update(self, instance, validated_data):
        if "lawyer" in validated_data and validated_data["lawyer"] is not None:
            validated_data.setdefault("status", Case.Status.ASSIGNED)
        return super().update(instance, validated_data)

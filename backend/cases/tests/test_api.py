import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIClient
from cases.models import Case


@pytest.mark.django_db
def test_anonymous_client_can_submit_case_without_account():
    api = APIClient()
    response = api.post("/api/cases/", {"title": "Umowa", "description": "Opis sprawy"}, format="json")

    assert response.status_code == 201
    case = Case.objects.get(pk=response.data["id"])
    assert case.client is None
    assert case.title == "Umowa"


@pytest.mark.django_db
def test_lawyer_sees_only_assigned_cases():
    lawyer_group, _ = Group.objects.get_or_create(name="Lawyer")
    lawyer = User.objects.create_user(username="lawyer", password="secret")
    lawyer_group.user_set.add(lawyer)

    other_lawyer_group, _ = Group.objects.get_or_create(name="Lawyer")
    other_lawyer = User.objects.create_user(username="other-lawyer", password="secret")
    other_lawyer_group.user_set.add(other_lawyer)

    Case.objects.create(client=None, title="Moja sprawa", description="Treść", lawyer=lawyer)
    Case.objects.create(client=None, title="Inna sprawa", description="Inna", lawyer=other_lawyer)

    api = APIClient()
    api.force_authenticate(lawyer)
    listing = api.get("/api/cases/")

    assert listing.status_code == 200
    assert len(listing.data) == 1
    assert listing.data[0]["title"] == "Moja sprawa"


@pytest.mark.django_db
def test_only_admin_can_assign_lawyer():
    lawyer_group, _ = Group.objects.get_or_create(name="Lawyer")
    lawyer = User.objects.create_user(username="lawyer", password="secret")
    lawyer_group.user_set.add(lawyer)

    admin_group, _ = Group.objects.get_or_create(name="Administrator")
    admin = User.objects.create_user(username="admin", password="secret")
    admin.is_staff = True
    admin.save()
    admin_group.user_set.add(admin)

    case = Case.objects.create(client=None, title="Sprawa", description="Treść")

    api = APIClient()
    api.force_authenticate(lawyer)
    assert api.patch(f"/api/cases/{case.id}/", {"lawyer": lawyer.id}, format="json").status_code == 404

    api.force_authenticate(admin)
    response = api.patch(f"/api/cases/{case.id}/", {"lawyer": lawyer.id}, format="json")
    assert response.status_code == 200
    assert response.data["lawyer"] == lawyer.id

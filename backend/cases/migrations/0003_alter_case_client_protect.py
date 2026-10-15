import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("cases", "0002_alter_case_client")]
    operations = [migrations.AlterField(
        model_name="case", name="client",
        field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="submitted_cases", to="auth.user"),
    )]

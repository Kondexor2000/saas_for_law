from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("cases", "0003_alter_case_client_protect")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="client_phone",
            field=models.CharField(default="", max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="case",
            name="client_email",
            field=models.EmailField(default="", max_length=254),
            preserve_default=False,
        ),
    ]

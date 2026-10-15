from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("cases", "0004_case_client_contact")]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE "cases_case" ALTER COLUMN "client_id" DROP NOT NULL',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
